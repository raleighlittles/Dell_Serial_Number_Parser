import dell_service_tag_parser

def test_simple_serial_number_parsing_test():


    serial_number = "CN-0006HY-PRC00-28H-A1RZ-A01"

    parsed_service_tag_obj = dell_service_tag_parser.parse_service_tag(serial_number)

    assert parsed_service_tag_obj["Country_of_manufacture"] == "China"
    assert parsed_service_tag_obj["Dell_part_number"] == "0006HY"
    assert parsed_service_tag_obj["Dell_Reserved_1"] == "PRC00"
    assert parsed_service_tag_obj["Dell_Reserved_2"] == "A1RZ"