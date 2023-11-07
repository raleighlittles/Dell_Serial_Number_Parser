import csv
import datetime
import time
import typing
# locals
import dell_serial_number_parser


def add_date_info_to_serial_number_obj(serial_number: typing.Dict) -> typing.Dict:

    curr_timestamp = datetime.datetime.now()

    curr_epoch = curr_timestamp.strftime("%s")
    curr_datetime = curr_timestamp.strftime("%Y-%m-%d")

    serial_number["Date_parsed"] = curr_datetime
    serial_number["timestamp"] = curr_epoch

    return serial_number


if __name__ == "__main__":

    serial_numbers_list = []

    with open("serial_numbers.txt", "r") as serial_numbers_file:

        for line_num, line_content in enumerate(serial_numbers_file):
            serial_number_dict_obj = dell_serial_number_parser.parse_serial_number(
                line_content.strip())

            serial_number_dict_obj["id"] = line_num
            serial_number_dict_obj = add_date_info_to_serial_number_obj(
                serial_number_dict_obj)

            serial_numbers_list.append(serial_number_dict_obj)
            time.sleep(1)

    with open("serial_numbers.csv", "w") as csv_file:

        csv_writer = csv.DictWriter(csv_file, serial_numbers_list[0].keys())

        csv_writer.writeheader()

        for serial_number_num, serial_number in enumerate(serial_numbers_list):

            csv_writer.writerow(serial_number)
