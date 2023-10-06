from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
)
import math

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp ,Optional
import email_validator
from flask_login import current_user
from wtforms import ValidationError,validators
from models import User


class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=8)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )


class register_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 8),
            EqualTo("pwd", message="Passwords must match !"),
        ]
    )


    def validate_email(self, email):
        print("validating mail")

        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered!")

    def validate_uname(self, uname):
        print("validating unma")
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken!")
        
    def validate_pwd(self, pwd):
        print("validating gcd")
        ascii_val = ""
        for character in pwd.data:
                ascii_val = ascii_val + str(format((ord(character)), '08b'))
        dec_len1 = int(ascii_val[:20], base=2)
        dec_len2 = int(ascii_val[20:41], base=2)
        dec_len3 = int(ascii_val[41:], base=2)
        # jjjjjjjj donne un gcd de 6
        gcd_len = math.gcd(dec_len1, dec_len2, dec_len3)
        if gcd_len > 1:
        #if math.gcd(2, 4, 16) > 1:
            err_msg= "gcd check NOK, GCD=" + str(gcd_len)
            raise ValidationError(err_msg)

