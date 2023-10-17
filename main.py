# Copyright 2023 Alex Neiman all rights reserved
# Equipment move software tool

DEBUG_MODE = True

from src.splmove import *
from src.file_tools import *
from src.npl import *
import shutil
import os

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
        print("Please fill out the excel template.")
        open_file_in_windows(filename)
        input("Press enter when you have saved and closed. [enter] ")




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

    # We now have a list of the following structure
    # [ datetime of lab time,
    #   week no.,
    #   is a holiday[t/f],
    #   lab section info,
    #   {info dictionary}   ]
    # sort by datetime first, then alphabetically by section
    # full_schedule.sort(key=lambda x: x[0])
    # full_schedule.sort(key=lambda x: x[3])

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
                "{}WK{}".format(course, week)
            ]
            write_row("Equipment", data, filename)


    # for labs in full_schedule:
    #     # full datetime schedule gets written to Equipment tab
    #     data = [
    #         labs[3], # lab and section
    #         labs[1], # Week
    #         ("" if not labs[2] else "Holiday (no lab)"),
    #         "DE{}".format(labs[3]), #Short code (DE342-01)
    #         ]
    #     write_row("Equipment", data, filename)

    open_file_in_windows(filename)





