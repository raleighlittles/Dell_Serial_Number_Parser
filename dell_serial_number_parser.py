# Filename: parse_dell_serial_number.py
#
# Date: 2023-10-26
# Author: Raleigh Littles <raleighlittles@gmail.com>
#
#

import datetime
import iso3166


def get_country_name_from_country_code(country_name: str) -> str:

    return iso3166.countries.get(country_name).name


def get_likeliest_mfg_date(serial_number_date: str) -> str:

    mfg_month = int(serial_number_date[1], 16)
    mfg_day = int(serial_number_date[2], 32)

    last_char_of_mfg_year = serial_number_date[0]

    current_timestamp = datetime.datetime.today()

    curr_year, curr_month, curr_day = current_timestamp.year, current_timestamp.month, current_timestamp.day
    last_char_of_current_year = str(curr_year)[-1]

    mfg_year = 0

    # With only the last character of the manufacturing year known,
    # we assume that the most likely mfg date is the closest possible to the current year.
    # for example, if it's 2023, and our product's last year digit is a 2, we'll assume it
    # was manufactured in 2022.
    # If the last year digit is a 4, we'd assume it was made in 2014, (obviously
    # the date cannot be in the future).
    # Where things get tricky is if the last char of the year matches ours.
    # Then, we'd look at the month, or if needed, day, to verify.

    if last_char_of_mfg_year == last_char_of_current_year:
        if (curr_month > mfg_month):
            mfg_year = curr_year

        elif (mfg_month > curr_month):
            # Must've been manufactured a decade (10 years) ago
            mfg_year = curr_year - 10

        else:  # mfg_month == curr_month
            if (curr_day > mfg_day):
                mfg_year = curr_year

            elif (mfg_day > curr_day):
                mfg_year = curr_year - 10

            else:  # mfg_day == curr_day
                # Could not have been manufactured today. Must have been on this
                # exact day 10 years ago
                mfg_year = curr_year - 10

    elif (last_char_of_current_year > last_char_of_mfg_year):
        # Was made earlier this decade
        mfg_year = str(curr_year)[0:3] + last_char_of_mfg_year

    else:  # last_char_of_mfg_year > last_char_of_current_year

        # Was made in the previous decade, ie. if current year is 2023, last_char_.. is 5
        # the latest it could've been made was 2015 [202-1=201]
        mfg_year = str(int(str(curr_year)[0:3]) - 1) + last_char_of_mfg_year

    # Needs the '-' prefix in formatting because the days/months aren't zero padded
    return f"{mfg_year}-{mfg_month}-{mfg_day}"


def parse_serial_number(serial_number: str) -> dict:

    serial_number_len = len(serial_number)

    min_serial_number_len, max_serial_number_len = 24, 30

    if (serial_number_len < min_serial_number_len) or (serial_number_len
                                                   > max_serial_number_len):
        raise ValueError(f"Serial number {serial_number} has invalid length of ",
                         serial_number_len)

    separator = "-"

    num_sections = serial_number.count(separator)

    country_code, part_number, mfg_date_str = "", "", ""

    # Older serial numbers that I found online had this format,
    # and this is what the documentation online mentions:
    # https://telcontar.net/KBK/Dell/date_codes
    # https://www.partschase.com/index.php?route=forum/read&forum_path=9&forum_post_id=45
    if num_sections == 4:
        country_code, part_number, dell_reserved_1, mfg_date_str, dell_reserved_2 = serial_number.split(
            separator)

    # Newer Dell serial numbers have an extra field, which I have not seen documented anywhere yet.
    # I don't know when this switch started happening.
    elif num_sections == 5:
        country_code, part_number, dell_reserved_1, mfg_date_str, dell_reserved_2, dell_reserved_3_opt = serial_number.split(
            separator)

    country = get_country_name_from_country_code(country_code)
    likely_mfg_date = get_likeliest_mfg_date(mfg_date_str)

    # print(f"Country: {country}")
    # print(f"Likeliest mfg date: {likely_mfg_date}")
    # print(f"Dell part number: {part_number}")

    return dict({
        "Country_of_manufacture": country,
        "Likeliest_manufacture_date": likely_mfg_date,
        "Dell_part_number": part_number,
        "Dell_Reserved_1": dell_reserved_1,
        "Dell_Reserved_2": dell_reserved_2,
        "original": serial_number
    })


serial_number_list = [
    "CN-06TFFF-75661-48B-0237-A00", "CN-0FWCRC-48661-355-1YZG-A02",
    "CN-0WW4XY-48661-59U-4HB6-A05", "CN-00J5C6-12966-7CR-01EE-A05",
    "CN-0WW4XY-48661-5A6-4O0V-A05", "CN-0DJ491-71581-3AI-025O"
]

for serial_number in serial_number_list:
    print("------------------------------")
    parse_serial_number(serial_number)
    print("------------------------------")
