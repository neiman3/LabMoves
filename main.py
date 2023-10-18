# Copyright 2023 Alex Neiman all rights reserved
# Equipment move software tool
from src.helpers import generate_lab_times
from src.splmove import *
from src.file_tools import *
import shutil
import os

DEBUG_MODE = True


def default_shortcode(week, course):
    return "{}WK{}".format(course, week)


if __name__ == "__main__":
    # main flow
    project_root = get_project_root()

    # get templates file and make data graph
    filename = os.path.join(project_root, 'templates', 'lab_rooms_layout.dat')
    if os.path.exists(filename):
        data = read_links(os.path.join(filename))

    # check output files folder is ther
    filename = os.path.join(project_root, 'Output Files')
    if not os.path.exists(filename):
        os.makedirs(filename)
        # make the dir
    else:
        if not os.path.isdir(filename):
            raise FileExistsError("{} is not a directory. Please delete".format(filename))

    # duplicate the excel template
    # ask for project name
    while True:
        if not DEBUG_MODE:
            failed = False
            project_name = input('Project name > ')
            for char in '!@#$%^&*{}|\`~ ':
                if char in project_name:
                    # there is a problem
                    print("Project name contains illegal character(s) ('{}').".format(char))
                    failed = True
            filename = os.path.join(project_root, 'Output Files', project_name + '.xlsx')
            if os.path.exists(filename):
                # does not exist
                failed = True
                print("Project already exists. Please delete it or choose a different name.")
            if failed:
                continue
        else:
            filename = os.path.join(project_root, 'Output Files', 'test3.xlsx')
        # filename ok
        # copy the excel template
        fromfn = os.path.join(project_root, 'templates', 'filled_template.xlsx')
        shutil.copyfile(fromfn, filename)
        break

    if not DEBUG_MODE:
        user_edit(filename)

    # Read lab teech employee schedule
    lab_tech_schedule = read_labtech_schedule(filename)
    # Get quarter dates from sections
    (quarter_start, quarter_end, sections_list) = read_sections(filename)
    holidays = read_holidays(filename)
    # Get list of course numbers
    courses = list_classes(sections_list)
    courses.sort()

    # Get SPL inventory
    base_inventory = read_inventory(filename)

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

    full_schedule = []
    for section in sections_list.keys():
        day = sections_list[section]['day']
        start_time = sections_list[section]['time']
        full_schedule += ([[i for i in j] + [section, sections_list[section]] for j in
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

    user_edit(filename, "Please fill out the default equipment schedule.")

    # Before we fill the default schedule we need to find the shortcodes associated with the
    # default schedules
    default_equipment_LUT = read_default_equipment_schedule(filename)
    # Now we can iterate through the full list of labs and check their equipment schedule
    for i in range(len(full_schedule)):
        event = full_schedule[i]
        # write to Modifications tab
        course = event[3].split('-')[0]
        shortcode = default_shortcode(event[1], course)
        inventory = Inventory()

        # Look up the full shortcode evalutaion
        if shortcode in default_equipment_LUT:
            equipments = default_equipment_LUT[shortcode]
        inventory
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
            event[0],  # date and time
            # shortcode for default equipment

        ]
        # write_row(ws_tab_name="Modifications", data=data, filename=filename)

    open_file_in_windows(filename)
