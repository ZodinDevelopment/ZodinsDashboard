from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import User



class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username.self.username.data).first()
            if user is not None:
                raise ValidationError("Please choose a different username.")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    post = TextAreaField("Say something", validators=[DataRequired()])
    submit = SubmitField("Post")



class ServiceForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Full Name", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=0, max=512)])
    submit = SubmitField("Contact")


class MessageForm(FlaskForm):
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField("Send")


class UploadForm(FlaskForm):
    pass
    
