import flask_wtf
import wtforms

class SubmitServiceTagForm(flask_wtf.FlaskForm):

    service_tag = wtforms.StringField("service_tag", validators=[wtforms.validators.DataRequired()])
    #recaptcha = flask_wtf.RecaptchaField()
    submit = wtforms.SubmitField("Submit")