
import flask
import csv
import flask_sqlalchemy
import datetime
import socket

def initialize_db(database):

    with open("service_tags.csv", "r") as csv_file:

        csv_reader = csv.DictReader(csv_file)

        for row_num, row_contents in enumerate(csv_reader):
            if row_num == 0:
                continue # skip column headers

            else:
                service_tag = ServiceTag(service_tag_id = row_contents["id"], 
                                    mfg_country = row_contents["Country_of_manufacture"],
                                    likely_mfg_date = row_contents["Likely_manufacture_date"],
                                    dell_part_number = row_contents["Dell_part_number"],
                                    dell_reserved_1 = row_contents["Dell_Reserved_1"],
                                    dell_reserved_2 = row_contents["Dell_Reserved_2"],
                                    service_tag = row_contents["original"],
                                    service_tag_id = row_contents["id"],
                                    datetime_parsed = datetime.datetime.strptime(row_contents["Date_parsed"], "%Y-%m-%d"),
                                    epoch_timestamp_parsed = row_contents["timestamp"])
                
                database.session.add(service_tag)

    database.session.commit()


class ServiceTag(database.Model):

    service_tag_id = database.Column(database.Integer, primary_key=True)
    mfg_country = database.Column(database.String, unique=False, nullable=False)
    likely_mfg_date = database.Column(database.DateTime, unique=False, nullable=False)
    dell_part_number = database.Column(database.String, unique=False, nullable=False)
    dell_reserved_1_field = database.Column(database.String, unique=False, nullable=False)
    dell_reserved_2_field = database.Column(database.String, unique=False, nullable=False)
    datetime_parsed = database.Column(database.DateTime, unique=False, nullable=True)
    service_tag = database.Column(database.String, unique=True, nullable=True)
    epoch_timestamp_parsed = database.Column(database.BigInt, unique=False, nullable=True)


if __name __ == "__main__":

    flask_instance_id = "".join(socket.hostname(), "__", __file__)
    app = flask.Flask(flask_instance_id)

    database_name = datetime.datetime.now().strftime("%Y%m%d") + "service_tags"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:////tmp/{database_name}.db"
    database = flask_sqlalchemy.SQLAlchemy(app)

    initialize_db(database)


@app.route("/service_tags/create", methods=["POST"])
def add_new_service_tag():

    # TODO fill in

                                

