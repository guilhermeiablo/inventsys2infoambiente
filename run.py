from flask import Flask, render_template, url_for, flash, redirect, request
from getpass import getpass
import requests
import json
from forms import LoginFormInventsys

app = Flask(__name__)

app.config['SECRET_KEY'] = '89247hrgr8ewr4uk'


def getprojetos():
	#Enviar request GET para receber um json com todos os ativos do projeto escolhido
	payload = {}
	headers = {
    
  		'Account': 'stesa',
  		'Token': mytoken,
	}
	prjurl = 'https://api.inventsys.com.br/v4/projects'
	projetos = requests.request('GET', prjurl, headers=headers, data=payload, allow_redirects=False)
	listaprojetos = projetos.json()['projects']


def selectprojeto():
	import ipywidgets as widgets
	from ipywidgets import interact


	variavelprj=""
	listaprj=[]
	for i in range(0,len(projetos.json()['projects'])):
	    prj=(projetos.json()['projects'][i]['id'])
	    nome=(projetos.json()['projects'][i]['name'])
	    variavelprj=(str(prj))
	    listaprj.append(variavelprj)

	print('Informa ID do projeto no inventsys: ')

	menuprj = widgets.Dropdown(
	    options=listaprj,
	    value='10762',
	    description='Projeto:',
	)


	menuprj

	botaoprojeto=widgets.Button(
	    description='Submeter',
	    disabled=False,
	    button_style='', # 'success', 'info', 'warning', 'danger' or ''
	    tooltip='Click me',
	    icon='check'
	)


	outputprojeto = widgets.Output()

	display(menuprj, botaoprojeto, outputprojeto)
	outputprojeto
	projectid=''
	def on_button_clicked_prj(b):
	    global projectid
	    with outputprojeto:
	        projectid = menuprj.value
	        print('Projeto selecionado: '+projectid)
        


	botaoprojeto.on_click(on_button_clicked_prj)


def getcategorias():
	caturl = 'https://api.inventsys.com.br/v4/projects/'+projectid+'/categories'
	categorias = requests.request('GET', caturl, headers=headers, data=payload, allow_redirects=False)
	#print(categorias.json()['categories'])


def selectcategoria():
	catvariavel=""
	catlista=[]
	for i in range(0,len(categorias.json()['categories'])):
		cat=(categorias.json()['categories'][i]['id'])
		nome=(categorias.json()['categories'][i]['name'])
		catvariavel=(str(cat))
		catlista.append(catvariavel)

	print('Informa ID da categoria no inventsys: ')
	menucat = widgets.Dropdown(
	    options=catlista,
	    value=catlista[0],
	    description='Categoria:',
	)


	menucat

	botaocat=widgets.Button(
	    description='Submeter',
	    disabled=False,
	    button_style='', # 'success', 'info', 'warning', 'danger' or ''
	    tooltip='Click me',
	    icon='check'
	)


	outputcat = widgets.Output()

	display(menucat, botaocat, outputcat)

	categoryid=''
	def on_button_clicked_cat(b):
	    global categoryid
	    with outputcat:
	        categoryid = menucat.value
	        print('Categoria selecionada: '+categoryid)

	botaocat.on_click(on_button_clicked_cat)


def getregistros():
	page = 1
	registros = []
	while True:
	    try:
	        url = 'https://api.inventsys.com.br/v4/projects/'+projectid+'/items?category='+categoryid+'&pagesize=1&page='+str(page)
	        ativos = requests.request('GET', url, headers=headers, data=payload, allow_redirects=False)
	        
	        
	        
	                
	        #print(ativos.json()['items'])
	        registros = registros + ativos.json()['items']
	        
	        #Se quiser ver os dados estruturados na resposta completa:
	        #print(ativos.text)
	        
	        #Se quiser ver os headers:
	        #print(ativos.headers)
	    except HTTPError:
	        # handle HTTPError
	        logging.error('HTTPError')
	    # ... put any other Exception you need to handle here
	    except IndexError:
	        break
	    except Exception as e:
	        # for handle unknown exception
	        logging.error('Unknown exception')
	    else:
	        if len(ativos.json()['items'])==0:
	            break
	        else:
	            page += 1

	print(registros)


def connecttopostgres():
	import psycopg2
	from psycopg2 import sql

	#Abrir os trabalhos para trabalhar com Postgres. Criar conexão e cursor como base.
	#conn = psycopg2.connect("host=localhost dbname=postgres user=guilhermeiablonovski")
	#cur = conn.cursor()



	hostinput = input('Informa host (localhost): ')
	dbnameinput = input('Informa dbname (postgres): ')
	userinput = input('Informa user (guilhermeiablonovski): ')


	#Define our connection string
	conn_string = "host="+str(hostinput)+" dbname="+str(dbnameinput)+" user="+str(userinput)
	 
	# print the connection string we will use to connect
	print('Connecting to database->%s' % (conn_string))
	 
	# get a connection, if a connect cannot be made an exception will be raised here
	conn = psycopg2.connect(conn_string)
	 
	# conn.cursor will return a cursor object, you can use this cursor to perform queries
	cur = conn.cursor()
	print('Connected!\n')


def createtable():
	dropdbgenerica = """DROP TABLE IF EXISTS {}""" 


	createdbgenerica = """CREATE UNLOGGED TABLE IF NOT EXISTS {}(
	id integer PRIMARY KEY,
	created_at DATE,
	updated_at DATE,
	name text,
	image text,
	project text,
	category_id integer,
	category_name text,
	latitude real,
	longitude real
	);""" 

	nometabela=projectid+'_'+categoryid



	dbobracorrente = """DROP TABLE IF EXISTS egrfauna_obracorrente;
	CREATE UNLOGGED TABLE IF NOT EXISTS egrfauna_obracorrente(
	id integer PRIMARY KEY,
	created_at DATE,
	updated_at DATE,
	name text,
	image text,
	project text,
	category_id integer,
	category_name text,
	latitude real,
	longitude real,
	tipo text,
	dimensao_passagem text,
	grau_obstrucao integer,
	natureza_obstrucao text
	);""" 


	dbobraespecial = """DROP TABLE IF EXISTS egrfauna_obraespecial;
	CREATE UNLOGGED TABLE IF NOT EXISTS egrfauna_obraespecial(
	id integer PRIMARY KEY,
	created_at DATE,
	updated_at DATE,
	name text,
	image text,
	project text,
	category_id integer,
	category_name text,
	latitude real,
	longitude real,
	tipo text,
	largura_passagem real,
	altura_passagem real,
	margem_seca text,
	grau_obstrucao text,
	natureza_obstrucao text,
	);""" 


	dbarmadilhas = """DROP TABLE IF EXISTS egrfauna_armadilhas;
	CREATE UNLOGGED TABLE IF NOT EXISTS egrfauna_armadilhas(
	id integer PRIMARY KEY,
	created_at DATE,
	updated_at DATE,
	name text,
	image text,
	project text,
	category_id integer,
	category_name text,
	latitude real,
	longitude real,
	observacoes text,
	instalacao DATE,
	IDcartao text,
	IDcamera text,
	IDbueiro text,
	estrada text,
	foto_armadilha text,
	gps_lat real,
	gps_long real,
	gps_alt real,
	gps_acc real);""" 
	    

	dbatropelamentos = """DROP TABLE IF EXISTS egrfauna_atropelamentos;
	CREATE UNLOGGED TABLE IF NOT EXISTS egrfauna_atropelamentos(
	id integer PRIMARY KEY,
	created_at DATE,
	updated_at DATE,
	name text,
	image text,
	project text,
	category_id integer,
	category_name text,
	latitude real,
	longitude real,
	estrada text,
	grupo text,
	esp_mamifero text,
	esp_ave text,
	esp_reptil text,
	esp_anfibio text,
	esp_outro text,
	idade text,
	estado text,
	posicao text,
	id_etiqueta text,
	nome_comum text,
	sexo text,
	observacoes text,
	ponto_gps text
	);"""



	if categoryid=='20685':
	    cur.execute(dbarmadilhas)
	else:
	    if categoryid=='20686':
	        cur.execute(dbatropelamentos)
	    else:
	        if categoryid=='18278':
	            cur.execute(dbobraespecial)
	        else:
	            if categoryid=='18284':
	                cur.execute(dbobracorrente)
	            else:
	                cur.execute(sql.SQL(dropdbgenerica)
	                            .format(sql.Identifier(nometabela)))
	                cur.execute(sql.SQL(createdbgenerica)
	                            .format(sql.Identifier(nometabela)))

	conn.commit()


def insertvalues():
	categoriasegr={'18284', '18278', '20685', '20686'}
	    


	if categoryid not in categoriasegr:
	    for item in registros:
	        genericfields=[
	            item['id'],
	            item['created_at'],
	            item['updated_at'],
	            item['name'],
	            item['image'],
	            item['project']['name'],
	            item['category_id'],
	            item['category']['name'],
	            item['location']['lat'],
	            item['location']['lng']
	        ]
	        my_data=[field for field in genericfields]
	        cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)").format(sql.Identifier(nometabela)),tuple(my_data))
	else:
	    print('.')
	    
	    
	if categoryid=='18284':
	        for item in registros:
	            obracorrentefields = [
	            item['id'],
	            item['created_at'],
	            item['updated_at'],
	            item['name'],
	            item['image'],
	            item['project']['name'],
	            item['category_id'],
	            item['category']['name'],
	            item['location']['lat'],
	            item['location']['lng'],
	            item['info'][0]['value'],
	            item['info'][1]['value'],
	            item['info'][2]['value'],
	            item['info'][3]['value']
	            ]
	            my_data = [field for field in obracorrentefields]
	            cur.execute("INSERT INTO egrfauna_obracorrente VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(my_data))
	else:
	    print('.')


	if categoryid=='18278':
	    for item in registros:
	        obraespecialfields = [
	        item['id'],
	        item['created_at'],
	        item['updated_at'],
	        item['name'],
	        item['image'],
	        item['project']['name'],
	        item['category_id'],
	        item['category']['name'],
	        item['location']['lat'],
	        item['location']['lng'],
	        item['info'][0]['value'],
	        item['info'][1]['value'],
	        item['info'][2]['value'],
	        item['info'][3]['value'],
	        item['info'][4]['value'],
	        item['info'][5]['value']
	        ]
	        my_data = [field for field in obraespecialfields]
	        cur.execute("INSERT INTO egrfauna_obraespecial VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(my_data))
	else:
	    print('.')



	if categoryid=='20685':
	    for item in registros:
	        armadilhafields = [
	        item['id'],
	        item['created_at'],
	        item['updated_at'],
	        item['name'],
	        item['image'],
	        item['project']['name'],
	        item['category_id'],
	        item['category']['name'],
	        item['location']['lat'],
	        item['location']['lng'],
	        item['info'][0]['value'],
	        item['info'][1]['value'],
	        item['info'][2]['value'],
	        item['info'][3]['value'],
	        item['info'][4]['value'],
	        item['info'][5]['value'],
	        item['info'][6]['value'],
	        item['info'][7]['value'],
	        item['info'][8]['value'],
	        item['info'][9]['value'],
	        item['info'][10]['value'],
	        ]
	        my_data = [field for field in armadilhafields]
	        cur.execute("INSERT INTO egrfauna_armadilhas VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(my_data))
	else:
	        print('.')
	    
	if categoryid=='20686':
	    for item in registros:
	        atropelamentofields = [
	        item['id'],
	        item['created_at'],
	        item['updated_at'],
	        item['name'],
	        item['image'],
	        item['project']['name'],
	        item['category_id'],
	        item['category']['name'],
	        item['location']['lat'],
	        item['location']['lng'],
	        item['info'][0]['value'],
	        item['info'][1]['value'],
	        item['info'][2]['value'],
	        item['info'][3]['value'],
	        item['info'][4]['value'],
	        item['info'][5]['value'],
	        item['info'][6]['value'],
	        item['info'][7]['value'],
	        item['info'][8]['value'],
	        item['info'][9]['value'],
	        item['info'][10]['value'],
	        item['info'][11]['value'],
	        item['info'][12]['value'],
	        item['info'][13]['value'],
	        item['info'][14]['value']
	        ]
	        my_data = [field for field in atropelamentofields]
	        cur.execute("INSERT INTO egrfauna_atropelamentos VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tuple(my_data))
	else:
	    print('.')
	    
	conn.commit()
	    
	    
	    

@app.route("/")
def home():
	return render_template("home.html")
    
@app.route("/about")
def about():
    return render_template("about.html")

mytoken='a'

@app.route("/login", methods=['GET', 'POST'])
def validateinventsys():
	form = LoginFormInventsys()
	if form.validate_on_submit():

		url = 'https://api.inventsys.com.br/v4/login'
		payload = "{\n  \"username\": \"" + form.username.data + "\",\n  \"password\": \"" + form.password.data + "\"\n}"
		headers = {
	  		'Account': 'stesa',
	  		'Content-Type': 'application/json',
		}
		r = requests.request('POST', url, headers = headers, data = payload, allow_redirects=False)
		r


		if r:
			global mytoken
			mytoken = r.json()['token']
			flash(f'Login realizado com sucesso para {form.username.data}!', 'success')
			return redirect(url_for('selectproject', mytoken=mytoken))
		else:
			flash('Login não realizado. Verifique o usuário e a senha.', 'danger')
	return render_template('logininventsys.html', title='LoginInventsys', form=form)


@app.route("/selectproject", methods=['GET', 'POST'])
def selectproject():
	global mytoken
	payload = {}
	headers = {
    
  		'Account': 'stesa',
  		'Token': mytoken,
	}
	prjurl = 'https://api.inventsys.com.br/v4/projects'
	projetos = requests.request('GET', prjurl, headers=headers, data=payload, allow_redirects=False)
	listaprojetos = projetos.json()['projects']

	variavelprj=""
	variavelnome=""
	listaprj=[]
	listanomes=[]
	for i in range(0,len(projetos.json()['projects'])):
	    prj=(projetos.json()['projects'][i]['id'])
	    nome=(projetos.json()['projects'][i]['name'])
	    variavelprj=(str(prj))
	    listaprj.append(variavelprj)
	    variavelnome=(str(nome))
	    listanomes.append(variavelnome)
	tulpa = [(x, y) for x, y in zip(listaprj, listanomes)]
	
	form = ProjectForm()
	form.selecionaprojeto.choices

	#form = UserDetails(request.POST, obj=tulpa)
	#form.group_id.choices = [(g.id, g.name) for g in Group.query.order_by('id')]

	return render_template('selectprojecto.html', title='SelectProject', mytoken=mytoken, listaprj=listaprj, tulpa=tulpa)
    
if __name__ == "__main__":
    app.run(debug=True)