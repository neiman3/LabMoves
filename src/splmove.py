from src.excel import *
from src.npl import *
import logging
import datetime


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
    start_date = ws['H4'].value
    end_date = ws['I4'].value

    # values
    # starting from row 4
    result = {}
    courses = [[i.value for i in r] for r in ws.iter_rows(min_row=4)]
    for course in courses:
        if None in course[0:6]:
            # ignore
            logging.warning("Malformed or missing data for course {}".format(course))
            continue
        course_shortcode = "{}-{:02d}".format(course[0], course[1])  # ex: 342-01 course and section
        instructor = course[2]
        room = ((course[3]) if type(course[3]) is int else (int(course[3])))
        day_of_week = resolve_day_of_week(course[4])
        time = course[5]
        result[course_shortcode] = {
            "instructor": instructor,
            "room": room,
            "day": day_of_week,
            "time": time
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
    holidays = [r[0].value for r in ws.iter_rows(min_row=4, min_col=11)]
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


def enumerate_day_of_week(text):
    text: str
    text2 = text.lower()
    lut = {
        "monday": 0,
        "mon": 0,
        "m": 0,
        "tuesday": 1,
        "tues": 1,
        "tue": 1,
        "t": 1,
        "wednesday": 2,
        "wed": 2,
        "w": 2,
        "thursday": 3,
        "thurs": 3,
        "thu": 3,
        "r": 3,
        "friday": 4,
        "fri": 4,
        "f": 4
    }
    if text2 in lut:
        return lut[text2]
    else:
        raise ValueError("Unable to resolve {} to a weekday. Please do not edit the template sheet.".format(text))


def generate_lab_times(day_of_week, start_time, quarter_start_date, quarter_end_date, holidays):
    # returns a list of tuples  [(datetime, week no, is_holiday)]
    pointer = quarter_start_date
    lab_day_of_week = enumerate_day_of_week(day_of_week)
    result = []
    week = 0
    while True:
        if pointer.weekday() == lab_day_of_week:
            # correct day
            is_holiday = False
            if pointer in holidays:
                is_holiday = True
                # it's not a holiday- continue
            result.append(((datetime.datetime.combine(pointer.date(), start_time)), week, is_holiday))
            pointer += datetime.timedelta(days=7)
            week += 1
        else:
            pointer += datetime.timedelta(days=1)
        if pointer > quarter_end_date:
            break

    return result
