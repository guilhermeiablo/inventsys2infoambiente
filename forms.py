from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length


class LoginFormInventsys(FlaskForm):
	username = StringField('Usuário', validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField('Senha', validators=[DataRequired()])
	remember = BooleanField('Salvar meus dados')
	submit= SubmitField('Enviar') 


class ProjectForm(FlaskForm):
    selecionaprojeto = SelectField('Operação')
    submit= SubmitField('Enviar') 


class CategoryForm(FlaskForm):
    selecionacategoria = SelectField('Categoria')
    submit= SubmitField('Enviar') 

class LoginFormPostgis(FlaskForm):
	hostinput = StringField('Host', validators=[DataRequired()])
	dbnameinput = StringField('Name', validators=[DataRequired()])
	userinput = StringField('Usuário', validators=[DataRequired()])
	senhainput= PasswordField('Senha')
	remember = BooleanField('Salvar meus dados')
	submit= SubmitField('Enviar') 


