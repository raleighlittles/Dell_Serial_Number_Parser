
import flask
import csv
import flask_sqlalchemy
import datetime
import socket
# locals
import forms


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
                                    datetime_parsed = datetime.datetime.strptime(row_contents["Date_parsed"], "%Y-%m-%d"),
                                    epoch_timestamp_parsed = row_contents["timestamp"])
                
                database.session.add(service_tag)

    database.session.commit()


flask_instance_id = "".join([socket.gethostname(), "__", __file__])
flask_app = flask.Flask(flask_instance_id, static_folder="static")
flask_app.config['SECRET_KEY'] = 'any secret string'

database_name = datetime.datetime.now().strftime("%Y%m%d") + "service_tags"
# Must be done before database can be instantiated
flask_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:////tmp/{database_name}.db"
database = flask_sqlalchemy.SQLAlchemy(flask_app)

@flask_app.route("/upload", methods=["GET", "POST"])
def add_new_service_tag():

    form = forms.SubmitServiceTagForm()

    if flask.request.method == "GET":
        return flask.render_template("submit.html", form=form)
    
    elif flask.request.method == "POST":
        if form.validate() == False:
            flask.flash("All fields are required!")
            return flask.render_template("submit.html", form=form)
        
        else: # form passes validation
            return '<h1>Service tag submitted!</h1>'

    # if form.validate_on_submit():
    #     return flask.redirect('/success')
    
    # return flask.render_template('submit.html', form=form)

                                
if __name__ == "__main__":

    print("Initializing database...")
    initialize_db(database)
    print("Initialization complete")

    print("Starting flask app...")
    flask_app.run(debug=True)
