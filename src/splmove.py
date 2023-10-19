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
    logging.debug("Read lab tech schedule from file")
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
    logging.debug("Read links structure from file")
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
                logging.warning("Malformed or missing data for course {}{}".format(course[0], (
                    (" ({})".format(course[2])) if course[2] is not None else "")))
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

    logging.debug("Read instructor schedule from file")
    return start_date, end_date, result


def read_inventory(filename):
    TAB_NAME = "Inventory"

    wb = load_wb(filename)
    ws = wb[TAB_NAME]
    items = [[i.value for i in r] for r in ws.iter_rows(min_row=4)]
    result = Inventory()
    for item in items:
        result.store(item[2], int(item[1]), str(item[0]))
    logging.debug("Read master inventory from file")
    return result


def read_holidays(filename):
    # returns a list of datetimes for each holiday
    TAB_NAME = "Sections"

    wb = load_wb(filename)
    ws = wb[TAB_NAME]
    holidays = [r[0].value for r in ws.iter_rows(min_row=4, min_col=12)]
    logging.debug("Read holiday schedule from file")
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
    result = {"HOLIDAY":{}}
    for row in rows:
        shortcode = row[0]
        if shortcode is None:
            continue
        result[shortcode] = {}
        for i in range(0, 8):
            if row[2 * i + 1] is not None:
                result[shortcode][row[2 * i + 1]] = row[2 * i + 2]
    logging.debug("Read default equipment schedule from file")
    return result


def encode_inventory(inventory):
    # Takes an inventory object and encodes it into a string
    # 2 x RB2, 1 x LCR [format]
    inventory: Inventory
    return ", ".join(["{} x {}".format(inventory.check(item), item) for item in inventory.inventory.keys()])


def decode_inventory(encoded_string, main_inventory: Inventory):
    # Takes a string  object and decodes it into an Inventory
    # 2 x RB2, 1 x LCR [format]
    if encoded_string is None:
        return Inventory()
    base = [i.split("x") for i in (encoded_string.replace(" ", "").split(","))]
    result = Inventory()
    for equipment in base:
        if equipment[1] == "HOLIDAY":
            continue
        try:
            result.store(equipment[1], int(equipment[0]), main_inventory.get_description(equipment[1]))
        except ValueError:
            logging.warning("Unable to parse equipment requirement {} on line {}".format(equipment, encoded_string))
    return result


def read_master_inventory_requirements(filename, master_inventory, full_schedule):
    # return a full_schedule updated with current inventory from Master Schedule sheet
    TAB_NAME = "Master Schedule"

    wb = load_wb(filename)
    ws = wb[TAB_NAME]
    rows = [[i.value for i in r] for r in ws.iter_rows(min_row=4)]
    for row in rows:
        inventory = decode_inventory(row[5], master_inventory)
        for i in range(len(full_schedule)):
            inventory_keys = inventory.inventory.keys()
            schedule_datetime = full_schedule[i][0]
            row_datetime = row[4]
            schedule_section = full_schedule[i][3]
            row_section = row[0]
            if schedule_datetime == row_datetime: # datetime matches
                if schedule_section == row_section: # section matches:
                    # Update the inventory
                    full_schedule[i][4]["inventory"] = inventory
                    break

    logging.debug("Read full schedule (custom inventory) from file")
    return full_schedule


def default_shortcode(week, course):
    return "{}WK{}".format(course, week)
