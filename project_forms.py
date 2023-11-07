import flask_wtf
import wtforms


class SubmitServiceTagForm(flask_wtf.FlaskForm):

    serial_number = wtforms.StringField(
        "serial_number", validators=[wtforms.validators.DataRequired()])
    #recaptcha = flask_wtf.RecaptchaField()
    submit = wtforms.SubmitField("Submit")
