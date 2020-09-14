from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import DateField


class LoginFormInventsys(FlaskForm):
	username = StringField('Usuário', validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField('Senha', validators=[DataRequired()])
	submit= SubmitField('Enviar') 


class ProjectForm(FlaskForm):
    selecionaprojeto = SelectField('Operação')
    submit= SubmitField('Enviar') 


class CategoryForm(FlaskForm):
    selecionacategoria = SelectField('Categoria')
    inicio = DateField('Data de início', format='%Y-%m-%d')
    fim = DateField('Data de fim', format='%Y-%m-%d')
    submit= SubmitField('Enviar') 

class LoginFormPostgis(FlaskForm):
	hostinput = StringField('Host', validators=[DataRequired()], default='infoambienteazure.postgres.database.azure.com')
	dbnameinput = StringField('Name', validators=[DataRequired()], default='postgres')
	userinput = StringField('Usuário', validators=[DataRequired()], default='infoambiente@infoambienteazure')
	senhainput= PasswordField('Senha')
	submit= SubmitField('Enviar') 

class LoginFormGeoserver(FlaskForm):
	urlgeoserver = StringField('URL REST Geoserver', validators=[DataRequired()], default='http://www.infoambiente.stesa.com.br:8080/geoserver/rest/')
	usrgeoserver = StringField('Usuário', validators=[DataRequired()], default='admin')
	pwdgeoserver = PasswordField('Senha', validators=[DataRequired()])
	workspace = StringField('Workspace', validators=[DataRequired()], default='InfoAmbiente')
	datastore = StringField('Datastore', validators=[DataRequired()], default='InfoambienteAzure')
	submit= SubmitField('Enviar') 

class LoginFormInfoambiente(FlaskForm):
	usrinfoambiente = StringField('Usuário', validators=[DataRequired()], default='admin')
	pwdinfoambiente = PasswordField('Senha', validators=[DataRequired()])
	submit= SubmitField('Enviar') 

class ProgramaForm(FlaskForm):
    selecionaprograma = SelectField('Programa Ambiental')
    novonome = StringField('Novo nome para camada no Infoambiente (opcional)')
    submit= SubmitField('Enviar') 



