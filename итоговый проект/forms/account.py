from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AccountForm(FlaskForm):
    new_task_field = TextAreaField('Новая задача', validators=[DataRequired()])
    name = TextAreaField("new_task_field")
    submit = SubmitField('Добавить')
