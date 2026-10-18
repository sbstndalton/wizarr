import re
from flask import has_request_context, request, session
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp

from app.forms.validators import (
    USERNAME_ALLOWED_CHARS_MESSAGE,
    USERNAME_LENGTH_MESSAGE,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_PATTERN,
    strip_filter,
)


class JoinForm(FlaskForm):
    username = StringField(
        "Username",
        filters=[strip_filter],
        validators=[
            DataRequired(),
            Length(
                min=USERNAME_MIN_LENGTH,
                max=USERNAME_MAX_LENGTH,
                message=USERNAME_LENGTH_MESSAGE,
            ),
            Regexp(USERNAME_PATTERN, message=USERNAME_ALLOWED_CHARS_MESSAGE),
        ],
    )
    email = StringField(
        "Email",
        filters=[strip_filter],
        validators=[Optional(), Email()],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(max=128, message="Password must be at most 128 characters."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    code = StringField(
        "Invite Code",
        filters=[strip_filter],
        validators=[DataRequired(), Length(min=6, max=10)],
        render_kw={"minlength": 6, "maxlength": 10},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if has_request_context() and request.method == "GET" and not self.username.data:
            code = (request.view_args or {}).get("code")
            saved = session.get("invite_prefill_username", "") if code == session.get("invite_prefill_code") else ""
            candidate = request.args.get("username", "") or saved
            candidate = re.sub(r"[^\w'.-]+", ".", candidate).strip(".")[:USERNAME_MAX_LENGTH]
            self.username.data = candidate.ljust(USERNAME_MIN_LENGTH, "_") if candidate else ""
