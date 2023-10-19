# Copyright 2023 Alex Neiman all rights reserved
# Equipment move software tool
from src.helpers import generate_lab_times, menu
from src.splmove import *
from src.file_tools import *
import logging
import shutil
import os
from src.splmove import default_shortcode

DEBUG_MODE = False
VERSION = 1
SUBVERSION = 3
SUB_SUBVERSION = None

if __name__ == "__main__":
    # set up logging
    logging.basicConfig(level=logging.WARNING)

    # main flow
    logging.info("User started equipment move software tool")
    logging.info(
        "Version {}.{}{}".format(VERSION, SUBVERSION, ("" if SUB_SUBVERSION is None else ".{}".format(SUB_SUBVERSION))))
    root_folder = get_project_root()
    logging.debug("Project root: {}".format(root_folder))

    # get templates file and make data graph
    filename = os.path.join(root_folder, 'templates', 'lab_rooms_layout.dat')
    if os.path.exists(filename):
        graph_structure = read_links(os.path.join(filename))
        logging.debug("Created Graph with anchor {}".format(graph_structure.home()))

    # check output files folder is ther
    filename = os.path.join(root_folder, 'Output Files')
    if not os.path.exists(filename):
        os.makedirs(filename)
        logging.debug("No output directory- created")
        # make the dir
    else:
        if not os.path.isdir(filename):
            logging.error("Output file directory not a directory")
            raise FileExistsError("{} is not a directory. Please delete".format(filename))
    # Menu
    menu_options = ["New project", "Open project"]
    user_choice = menu(menu_options)

    # duplicate the excel template
    # ask for project name
    if user_choice == 1:
        # Get a new file name
        while True:
            if not DEBUG_MODE:
                failed = False
                project_name = input('Project name > ')
                for char in '!@#$%^&*{}|\`~ ':
                    if char in project_name:
                        # there is a problem
                        print("Project name contains illegal character(s) ('{}').".format(char))
                        failed = True
                filename = os.path.join(root_folder, 'Output Files', project_name + '.xlsx')
                if os.path.exists(filename):  ## DEBUG
                    # does not exist
                    failed = True
                    print("Project already exists. Please delete it or choose a different name.")
                if failed:
                    continue
            else:
                filename = os.path.join(root_folder, 'Output Files', 'test3.xlsx')
            # filename ok
            logging.debug("User opened new project at {}".format(filename))
            # copy the excel template
            fromfn = os.path.join(root_folder, 'templates', 'filled_template.xlsx')
            shutil.copyfile(fromfn, filename)  ## DEBUG
            logging.debug("Copied {} -> {}".format(fromfn, filename))
            break
    else:
        # User wants to open existing file
        filename = file_prompt("Project name > ", base_dir=os.path.join(root_folder, 'Output Files'),
                               auto_filetype='xlsx', must_exist=True)

    if user_choice == 1:
        logging.debug("Waiting for user to edit initial class schedule")
        user_edit(filename, "STEP 1: Fill out tabs 1-3 (Techs, Sections, and Inventory).")
        logging.debug("User edited initial class schedule")

    # Read lab tech employee schedule
    lab_tech_schedule = read_labtech_schedule(filename)
    # Get quarter dates from sections
    (quarter_start, quarter_end, sections_list) = read_sections(filename)
    holidays = read_holidays(filename)
    # Get list of course numbers
    courses = list_classes(sections_list)
    courses.sort()

    # Get SPL inventory
    base_inventory = read_inventory(filename)
    graph_structure.anchor.inventory = base_inventory

    # If the user is making a new file:
    if user_choice == 1:
        # now let's fill the default schedule in the Equipment tab
        # We want to see each class and its week
        NO_WEEKS_DEFAULT = 11
        # We just assume the default schedule is 11 weeks
        for course in courses:
            for week in range(1, NO_WEEKS_DEFAULT + 1):
                # start at week 1
                data = [
                    course,
                    week,
                    "",
                    default_shortcode(week, course)
                ]
                write_row("Equipment", data, filename)

    # Holiday

    # Generate full schedule
    full_schedule = []
    for section in sections_list.keys():
        day = sections_list[section]['day']
        start_time = sections_list[section]['time']
        full_schedule += (
        [[i for i in j] + [section, {key: sections_list[section][key] for key in sections_list[section].keys()}] for j
         in
         generate_lab_times(day, start_time, quarter_start, quarter_end, holidays)])
    # We now have a list of the following structure
    # [ datetime of lab time,
    #   week no.,
    #   is a holiday[t/f],
    #   lab section info,
    #   {info dictionary}   ]
    # sort by datetime first, then alphabetically by section
    full_schedule.sort(key=lambda x: x[0])
    full_schedule.sort(key=lambda x: x[3])

    if user_choice == 1:
        # The user needs to edit the defaut schedule now
        user_edit(filename, "STEP 2: Add the default weekly equipment requirements on the Equipment tab")

    # Before we fill the default master schedule we need to find the shortcodes associated with the
    # default schedules
    default_equipment_LUT = read_default_equipment_schedule(filename)

    if user_choice == 1:
        # Now we can iterate through the full list of labs and check their equipment schedule
        for i in range(len(full_schedule)):
            event = full_schedule[i]
            # write to Modifications tab
            course = event[3].split('-')[0]
            shortcode = default_shortcode(event[1], course)
            inventory = Inventory()

            if event[2]:
                # It's a holiday
                equipments = {"HOLIDAY": 0}
            else:
                # Look up the full shortcode evalutaion
                if shortcode in default_equipment_LUT:
                    equipments = default_equipment_LUT[shortcode]

                    for equipment in equipments.keys():
                        required_qty = equipments[equipment]
                        # If it's negative, its a class
                        if required_qty is None:
                            continue
                        if required_qty < 0:
                            required_qty = -1 * required_qty
                        else:
                            required_qty = required_qty * event[4]['groups']
                        inventory.store(equipment, required_qty, base_inventory.get_description(equipment))
            # don't set that schedule to the events yet- user should modify it fist
            # full_schedule[i][4]['requirements'] = inventory

            data = [
                event[3],  # section and class no
                event[4]['instructor'],  # instructor
                event[1],  # week
                ("Holiday, no lab" if event[2] else ""),
                event[0],  # date and time
                # shortcode for default equipment
                encode_inventory(inventory)
            ]

            write_row(ws_tab_name="Master Schedule", data=data, filename=filename)

        user_edit(filename,
                  "STEP 3: Please modify any custom changes to the equipment list on the Master Schedule tab.")
        # Now that the user has written out the full equipment list, try to load it again

    full_schedule = read_master_inventory_requirements(filename, base_inventory, full_schedule)

    # Now we have a full schedule that has been edited by user with all equipment requirements
    # We now want to generate a schedule
    # This is a separate excel file that is a duplicate of output.xlsx
    # It's called [project-name]-output.xlsx
    filename = add_dash_tag(filename, 'output')
    if os.path.exists(filename):
        # delete existing output files
        os.remove(filename)
    source = os.path.join(root_folder, 'templates', 'output.xlsx')
    shutil.copyfile(source, filename)
    # Ready to fill out default schedule tab
    # datetime, week, course, section, instructor, room, note, equipment list
    for event in full_schedule:
        data = [
            event[0],  # datetime
            event[1],  # week no.
            event[3].split('-')[0],  # course
            event[3].split('-')[1],  # section
            event[4]['instructor'],
            event[4]['room'],
            ("Holiday" if event[2] else ""),  # note (if holiday)
            encode_inventory(event[4]['inventory'], full_description=True, master_inventory=base_inventory, sep=', ')
        ]
        write_row("Schedule", data, filename)

    # Generate the move schedule room requs by lab room
    # Left column is datetime, then each room has its equipment requirements in its own column
    room_reqs = {}
    # {datetime: {111: Inventory(), 112: Inventory...}}
    rooms = graph_structure.list_nodes()

    # Make a dictionary that holds every lab time with what room needs what equipment
    for event in full_schedule:
        lab_start_time = event[0]
        room = event[4]['room']
        equipment_needs: Inventory = event[4]['inventory']
        if lab_start_time in room_reqs:
            room_reqs[lab_start_time][room] = equipment_needs
        else:
            room_reqs[lab_start_time] = {room: equipment_needs}
    lab_times = [i for i in room_reqs.keys()]
    lab_times.sort()
    # write row labels to B3, C3, D3, etc.
    for i in range(len(rooms)):
        set_cell(1 + i, 3, rooms[i], filename, 'Moves')
    for time in lab_times:
        data = [time]
        for room in rooms:
            if room in room_reqs[time]:
                data.append(
                    encode_inventory(room_reqs[time][room], full_description=True, master_inventory=base_inventory,
                                     sep='\n'))
            else:
                data.append("")
        write_row('Moves', data, filename)

    wrap_cells(filename, 'Moves')

    # # Now generate the move schedule
    # # sort main schedule by datetime
    # moves = []
    # # Moves should have a list structure of this
    # # [datetime, Inventory() of items, from_room, to_room]
    # employees = {employee: 0 for employee in employees_from_schedule(lab_tech_schedule)}
    # # employees will hold everyone's name and how many moves they've done
    # full_schedule.sort(key=lambda x: x[0])
    # for event in full_schedule:
    #     lab_start_time = event[0]
    #     room = event[4]['room']
    #     equipment_needs: Inventory = event[4]['inventory']
    #
    #     continue

    open_file_in_windows(filename)
    print("Schedule generation complete")
