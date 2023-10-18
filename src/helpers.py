import datetime


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
    # returns a list of tuples  [(datetime, week no, is_holiday, section, data)]
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
