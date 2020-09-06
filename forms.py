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
	hostinput = StringField('Host', validators=[DataRequired()], default='localhost')
	dbnameinput = StringField('Name', validators=[DataRequired()], default='postgres')
	userinput = StringField('Usuário', validators=[DataRequired()], default='guilhermeiablonovski')
	senhainput= PasswordField('Senha')
	remember = BooleanField('Salvar meus dados')
	submit= SubmitField('Enviar') 

class LoginFormGeoserver(FlaskForm):
	urlgeoserver = StringField('URL REST Geoserver', validators=[DataRequired()], default='http://localhost:8080/geoserver/rest/')
	usrgeoserver = StringField('Usuário', validators=[DataRequired()], default='admin')
	pwdgeoserver = PasswordField('Senha', validators=[DataRequired()], default='geoserver')
	workspace = StringField('Workspace', validators=[DataRequired()], default='cite')
	datastore = StringField('Datastore', validators=[DataRequired()], default='newDatastoreName')
	remember = BooleanField('Salvar meus dados')
	submit= SubmitField('Enviar') 

class LoginFormInfoambiente(FlaskForm):
	usrinfoambiente = StringField('Usuário', validators=[DataRequired()], default='admin')
	pwdinfoambiente = PasswordField('Senha', validators=[DataRequired()])
	remember = BooleanField('Salvar meus dados')
	submit= SubmitField('Enviar') 



