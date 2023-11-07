import flask
import csv
import flask_sqlalchemy
import datetime
import sys
import socket
import sqlalchemy

# locals
import forms

import dell_service_tag_parser
import initialize_csv

flask_instance_id = "".join([socket.gethostname(), "__", __file__])
flask_app = flask.Flask(flask_instance_id, static_folder="static")
flask_app.config['SECRET_KEY'] = 'any secret string'

database_name = datetime.datetime.now().strftime("%Y%m%d") + "__service_tags"
# Must be done before database can be instantiated
flask_app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"sqlite:////tmp/{database_name}.db"
database = flask_sqlalchemy.SQLAlchemy(flask_app)


class ServiceTag(database.Model):
    service_tag_id = database.Column(database.String, primary_key=True)
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
    service_tag_original = database.Column(database.String,
                                           unique=True,
                                           nullable=False)
    epoch_timestamp_parsed = database.Column(database.BigInteger,
                                             unique=False,
                                             nullable=False)


def initialize_db(database):

    with open("service_tags.csv", "r") as csv_file:

        csv_reader = csv.DictReader(csv_file)

        for row_num, row_contents in enumerate(csv_reader):
            if row_num == 0:
                continue  # skip column headers

            else:
                service_tag = ServiceTag(
                    service_tag_id=row_contents["id"],
                    mfg_country=row_contents["Country_of_manufacture"],
                    likely_mfg_date=datetime.datetime.strptime(
                        row_contents["Likeliest_manufacture_date"],
                        "%Y-%m-%d"),
                    dell_part_number=row_contents["Dell_part_number"],
                    dell_reserved_1_field=row_contents["Dell_Reserved_1"],
                    dell_reserved_2_field=row_contents["Dell_Reserved_2"],
                    service_tag_original=row_contents["original"],
                    datetime_parsed=datetime.datetime.strptime(
                        row_contents["Date_parsed"], "%Y-%m-%d"),
                    epoch_timestamp_parsed=row_contents["timestamp"])

                print(f"Adding service tag with ID {row_contents['id']}")

                database.session.add(service_tag)

                database.session.flush()
        database.session.commit()


@flask_app.route("/upload", methods=["GET", "POST"])
def add_new_service_tag():

    flask_app.logger.info("add_new_service_tag() called")

    form = forms.SubmitServiceTagForm()

    if flask.request.method == "GET":
        return flask.render_template("submit.html", form=form)

    elif flask.request.method == "POST":
        if form.validate() == False:
            flask.flash("All fields are required!")
            return flask.render_template("submit.html", form=form)

        else:  # form passes validation
            flask_app.logger.info("Service tag submitted %s",
                                  form.service_tag.data)
            raw_service_tag = form.service_tag.data
            parsed_service_tag = dell_service_tag_parser.parse_service_tag(
                raw_service_tag)

            parsed_service_tag_with_date = initialize_csv.add_date_info_to_service_tag_obj(
                parsed_service_tag)

            next_id = database.session.query(ServiceTag).count() + 1
            flask_app.logger.info("Adding new item to table, with ID %s",
                                  next_id)

            mfg_country = parsed_service_tag_with_date[
                "Country_of_manufacture"]
            likely_mfg_date = datetime.datetime.strptime(
                parsed_service_tag_with_date["Likeliest_manufacture_date"],
                "%Y-%m-%d")
            dell_part_number = parsed_service_tag_with_date["Dell_part_number"]
            dell_reserved_1_field = parsed_service_tag_with_date[
                "Dell_Reserved_1"]
            dell_reserved_2_field = parsed_service_tag_with_date[
                "Dell_Reserved_2"]

            new_service_tag_obj = ServiceTag(
                service_tag_id=next_id,
                mfg_country=mfg_country,
                likely_mfg_date=likely_mfg_date,
                dell_part_number=dell_part_number,
                dell_reserved_1_field=dell_reserved_1_field,
                dell_reserved_2_field=dell_reserved_2_field,
                service_tag_original=raw_service_tag,
                datetime_parsed=datetime.datetime.strptime(
                    parsed_service_tag_with_date["Date_parsed"], "%Y-%m-%d"),
                epoch_timestamp_parsed=parsed_service_tag_with_date[
                    "timestamp"])

            next_id = (database.session.query(ServiceTag).count() + 1)

            try:
                database.session.add(new_service_tag_obj)
                database.session.commit()
                return flask.render_template(
                    "submission_successful.html",
                    submission_number=next_id,
                    original_service_tag=raw_service_tag,
                    likeliest_mfg_date=likely_mfg_date,
                    dell_part_number=dell_part_number,
                    dell_reserved_1=dell_reserved_1_field,
                    dell_reserved_2=dell_reserved_2_field)

            except sqlalchemy.exc.IntegrityError:

                # Tried to submit a service tag that already exists
                database.session.rollback()
                flask_app.logger.warn(
                    "Duplicate serial number received -- could not submit to database"
                )
                # Figure out when the serial number was originally submitted and let the user know
                original_serial_number_submission = ServiceTag.query.filter_by(
                    service_tag_original=raw_service_tag)

                return flask.render_template(
                    "submission_failed.html",
                    user_serial_number=raw_service_tag,
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
