import csv
import datetime
import time
import typing
# locals
import dell_service_tag_parser


def add_date_info_to_service_tag_obj(service_tag: typing.Dict) -> typing.Dict:

    curr_timestamp = datetime.datetime.now()

    curr_epoch = curr_timestamp.strftime("%s")
    curr_datetime = curr_timestamp.strftime("%Y-%m-%d")

    service_tag["Date_parsed"] = curr_datetime
    service_tag["timestamp"] = curr_epoch

    return service_tag


if __name__ == "__main__":

    service_tags_list = []

    with open("service_tags.txt", "r") as service_tags_file:

        for line_num, line_content in enumerate(service_tags_file):
            service_tag_dict_obj = dell_service_tag_parser.parse_service_tag(
                line_content.strip())

            service_tag_dict_obj["id"] = line_num
            service_tag_dict_obj = add_date_info_to_service_tag_obj(
                service_tag_dict_obj)

            service_tags_list.append(service_tag_dict_obj)
            time.sleep(1)

    with open("service_tags.csv", "w") as csv_file:

        csv_writer = csv.DictWriter(csv_file, service_tags_list[0].keys())

        csv_writer.writeheader()

        for service_tag_num, service_tag in enumerate(service_tags_list):

            csv_writer.writerow(service_tag)
