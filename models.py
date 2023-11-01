import main

class ServiceTag(main.database.Model):
    service_tag_id = database.Column(database.Integer, primary_key=True)
    mfg_country = database.Column(database.String, unique=False, nullable=False)
    likely_mfg_date = database.Column(database.DateTime, unique=False, nullable=False)
    dell_part_number = database.Column(database.String, unique=False, nullable=False)
    dell_reserved_1_field = database.Column(database.String, unique=False, nullable=False)
    dell_reserved_2_field = database.Column(database.String, unique=False, nullable=False)
    datetime_parsed = database.Column(database.DateTime, unique=False, nullable=True)
    service_tag = database.Column(database.String, unique=True, nullable=True)
    epoch_timestamp_parsed = database.Column(database.BigInt, unique=False, nullable=True)