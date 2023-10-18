from src.npl import *
from src.file_tools import *
import logging


# The excel sheet should read some stuff
def read_labtech_schedule(filename):
    TAB_NAME = "Techs"
    wb = load_wb(filename)
    ws = wb[TAB_NAME]
    cells_range = ws['B4':'F14']

    # base schedule
    result = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    for i in range(len(days)):
        day = days[i]
        theday = {}
        for j in range(len(hours)):
            hour = hours[j]
            theday[hour] = None
        result[day] = theday

    for i in range(len(cells_range)):
        row = cells_range[i]
        for j in range(len(row)):
            column = row[j]
            cell = column.value
            hour = hours[i]
            dayofweek = days[j]
            result[dayofweek][hour] = cell

    return result


def read_links(filename):
    # Import a linking file from a .dat text file
    result = None
    with open(filename) as f:
        for line in f:
            clean = ''
            for char in line:
                if char != '\n':
                    clean += char
            line = clean
            del clean

            if line == '':
                continue

            if line[0] == '#':
                # comment
                continue

            links = line.split(' ')

            if result is None:
                # very first line- make it anchor
                result = Graph(Node(int(links[0])))
                continue

            if len(links) != 3:
                raise ValueError("Malformed input file: {}, {}".format(filename, line))

            result.add(int(links[0]), int(links[1]), int(links[2]))
    return result


def read_sections(filename):
    TAB_NAME = "Sections"

    wb = load_wb(filename)
    ws = wb[TAB_NAME]

    # Read quarter start and end time
    start_date = ws['I4'].value
    end_date = ws['J4'].value

    # values
    # starting from row 4
    result = {}
    courses = [[i.value for i in r] for r in ws.iter_rows(min_row=4)]
    for course in courses:
        if None in course[0:7]:
            # ignore
            if course[0] is not None:
                logging.warning("Malformed or missing data for course {}{}".format(course[0], ((" ({})".format(course[2])) if course[2] is not None else "")))
            continue
        course_shortcode = "{}-{:02d}".format(course[0], course[1])  # ex: 342-01 course and section
        instructor = course[2]
        room = ((course[3]) if type(course[3]) is int else (int(course[3])))
        day_of_week = resolve_day_of_week(course[4])
        time = course[5]
        groups = course[6]
        result[course_shortcode] = {
            "instructor": instructor,
            "room": room,
            "day": day_of_week,
            "time": time,
            "groups": groups
        }

    return start_date, end_date, result


def read_inventory(filename):
    TAB_NAME = "Inventory"

    wb = load_wb(filename)
    ws = wb[TAB_NAME]
    items = [[i.value for i in r] for r in ws.iter_rows(min_row=4)]
    result = Inventory()
    for item in items:
        result.store(item[2], int(item[1]), str(item[0]))
    return result


def read_holidays(filename):
    # returns a list of datetimes for each holiday
    TAB_NAME = "Sections"

    wb = load_wb(filename)
    ws = wb[TAB_NAME]
    holidays = [r[0].value for r in ws.iter_rows(min_row=4, min_col=12)]
    return holidays


def resolve_day_of_week(text):
    text: str
    text2 = text.lower()
    lut = {
        "monday": "Monday",
        "mon": "Monday",
        "m": "Monday",
        "tuesday": "Tuesday",
        "tues": "Tuesday",
        "tue": "Tuesday",
        "t": "Tuesday",
        "wednesday": "Wednesday",
        "wed": "Wednesday",
        "w": "Wednesday",
        "thursday": "Thursday",
        "thurs": "Thursday",
        "thu": "Thursday",
        "r": "Thursday",
        "friday": "Friday",
        "fri": "Friday",
        "f": "Friday"
    }
    if text2 in lut:
        return lut[text2]
    else:
        raise ValueError("Unable to resolve {} to a weekday. Please do not edit the template sheet.".format(text))


def read_default_equipment_schedule(filename):
    # Open the Equipment tab
    # returns a LUT that can be used to enumerate default equipments
    # For example, the 295WK4 shortcode would return a dictionary of
    # requirements and quantity
    # {"RB2" : 3, "LCR", 1}

    TAB_NAME = "Equipment"

    wb = load_wb(filename)
    ws = wb[TAB_NAME]
    rows = [[i.value for i in r] for r in ws.iter_rows(min_row=4, min_col=4)]
    result = {}
    for row in rows:
        shortcode = row[0]
        if shortcode is None:
            continue
        result [shortcode] = {}
        for i in range(0,8):
            if row[2*i + 1] is not None:
                result[shortcode][row[2*i+1]] = row[2*i + 2]
    return result