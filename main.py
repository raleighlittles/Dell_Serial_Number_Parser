import csv
import datetime
import flask
import flask_sqlalchemy
import secrets
import string
import socket
import sqlalchemy
import sys

# locals
import project_forms
import dell_serial_number_parser
import initialize_csv

def generate_secret_key(length):
    password = ''.join(secrets.choice((string.ascii_letters + string.digits)) for i in range(length))
    return password

flask_instance_id = "".join([socket.gethostname(), "__", __file__])

flask_app = flask.Flask(flask_instance_id, static_folder="static")

# needed for CSRF
flask_app.config['SECRET_KEY'] = generate_secret_key(12)

database_name = datetime.datetime.now().strftime("%Y%m%d") + "__serial_numbers"
# Must be done before database can be instantiated
flask_app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"sqlite:////tmp/{database_name}.db"
database = flask_sqlalchemy.SQLAlchemy(flask_app)

class ServiceTag(database.Model):
    serial_number_id = database.Column(database.String, primary_key=True)
    mfg_country = database.Column(database.String,
                                  unique=False,
                                  nullable=False)
    likely_mfg_date = database.Column(database.DateTime,
                                      unique=False,
                                      nullable=False)
    dell_part_number = database.Column(database.String,
                                       unique=False,
                                       nullable=False)
    dell_reserved_1_field = database.Column(database.String,
                                            unique=False,
                                            nullable=False)
    dell_reserved_2_field = database.Column(database.String,
                                            unique=False,
                                            nullable=False)
    datetime_parsed = database.Column(database.DateTime,
                                      unique=False,
                                      nullable=False)
    serial_number_original = database.Column(database.String,
                                           unique=True,
                                           nullable=False)
    epoch_timestamp_parsed = database.Column(database.BigInteger,
                                             unique=False,
                                             nullable=False)


def initialize_db(database):

    with open("serial_numbers.csv", "r") as csv_file:

        csv_reader = csv.DictReader(csv_file)

        for row_num, row_contents in enumerate(csv_reader):
            if row_num == 0:
                continue  # skip column headers

            else:
                serial_number = ServiceTag(
                    serial_number_id=row_contents["id"],
                    mfg_country=row_contents["Country_of_manufacture"],
                    likely_mfg_date=datetime.datetime.strptime(
                        row_contents["Likeliest_manufacture_date"],
                        "%Y-%m-%d"),
                    dell_part_number=row_contents["Dell_part_number"],
                    dell_reserved_1_field=row_contents["Dell_Reserved_1"],
                    dell_reserved_2_field=row_contents["Dell_Reserved_2"],
                    serial_number_original=row_contents["original"],
                    datetime_parsed=datetime.datetime.strptime(
                        row_contents["Date_parsed"], "%Y-%m-%d"),
                    epoch_timestamp_parsed=row_contents["timestamp"])

                print(f"Adding serial number with ID {row_contents['id']}")

                database.session.add(serial_number)

                database.session.flush()
        database.session.commit()


@flask_app.route("/upload", methods=["GET", "POST"])
def add_new_serial_number():

    flask_app.logger.info("add_new_serial_number() called")

    form = project_forms.SubmitServiceTagForm()

    if flask.request.method == "GET":
        return flask.render_template("submit.html", form=form)

    elif flask.request.method == "POST":
        if form.validate() == False:
            flask.flash("All fields are required!")
            return flask.render_template("submit.html", form=form)

        else:  # form passes validation
            flask_app.logger.info("Serial number submitted %s",
                                  form.serial_number.data)
            raw_serial_number = form.serial_number.data
            parsed_serial_number = dell_serial_number_parser.parse_serial_number(
                raw_serial_number)

            parsed_serial_number_with_date = initialize_csv.add_date_info_to_serial_number_obj(
                parsed_serial_number)

            next_id = database.session.query(ServiceTag).count() + 1
            flask_app.logger.info("Adding new item to table, with ID %s",
                                  next_id)

            mfg_country = parsed_serial_number_with_date[
                "Country_of_manufacture"]
            likely_mfg_date = datetime.datetime.strptime(
                parsed_serial_number_with_date["Likeliest_manufacture_date"],
                "%Y-%m-%d")
            dell_part_number = parsed_serial_number_with_date["Dell_part_number"]
            dell_reserved_1_field = parsed_serial_number_with_date[
                "Dell_Reserved_1"]
            dell_reserved_2_field = parsed_serial_number_with_date[
                "Dell_Reserved_2"]

            new_serial_number_obj = ServiceTag(
                serial_number_id=next_id,
                mfg_country=mfg_country,
                likely_mfg_date=likely_mfg_date,
                dell_part_number=dell_part_number,
                dell_reserved_1_field=dell_reserved_1_field,
                dell_reserved_2_field=dell_reserved_2_field,
                serial_number_original=raw_serial_number,
                datetime_parsed=datetime.datetime.strptime(
                    parsed_serial_number_with_date["Date_parsed"], "%Y-%m-%d"),
                epoch_timestamp_parsed=parsed_serial_number_with_date[
                    "timestamp"])

            next_id = (database.session.query(ServiceTag).count() + 1)

            try:
                database.session.add(new_serial_number_obj)
                database.session.commit()
                return flask.render_template(
                    "submission_successful.html",
                    country_of_mfg=mfg_country,
                    submission_number=next_id,
                    original_serial_number=raw_serial_number,
                    likeliest_mfg_date=likely_mfg_date,
                    dell_part_number=dell_part_number,
                    dell_reserved_1=dell_reserved_1_field,
                    dell_reserved_2=dell_reserved_2_field)

            except sqlalchemy.exc.IntegrityError:

                # Tried to submit a serial number that already exists
                database.session.rollback()

                flask_app.logger.warn(
                    "Duplicate serial number received -- could not submit to database"
                )

                # Figure out when the serial number was originally submitted and let the user know
                original_serial_number_submission = ServiceTag.query.filter_by(
                    serial_number_original=raw_serial_number)

                return flask.render_template(
                    "submission_failed.html",
                    user_serial_number=raw_serial_number,
                    original_submission_date=original_serial_number_submission.
                    first().datetime_parsed)


# Flask doesn't use the __main__
# https://www.pythonanywhere.com/forums/topic/27053/

with flask_app.app_context():

    # Should not have to run this, but I get an error if I take it out
    database.drop_all()

    print("Initializing database...")
    database.create_all()

    initialize_db(database)
    print("Initialization complete")

    print("Starting flask app...")
    #flask_app.run(debug=True)
