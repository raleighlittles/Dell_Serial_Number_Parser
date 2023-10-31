
import flask
import csv
import flask_sqlalchemy
import datetime

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

database = flask_sqlalchemy.SQLAlchemy(app)

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

                                

