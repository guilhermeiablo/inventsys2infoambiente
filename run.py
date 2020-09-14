from flask import Flask, Blueprint, render_template, url_for, flash, redirect, request, jsonify, session
from flask_session import Session
#from flask_sqlalchemy import SQLAlchemy
from getpass import getpass
import random , string
import requests
import json
from forms import LoginFormInventsys, ProjectForm, CategoryForm, LoginFormPostgis, LoginFormGeoserver, LoginFormInfoambiente, ProgramaForm
import psycopg2
from psycopg2 import sql
import geoserver
from geoserver.catalog import Catalog
from geoserver.resource import FeatureType
import re
import datetime

app = Flask(__name__)


app.config['SECRET_KEY'] = '89247hrgr8ewr4uk'
SESSION_TYPE = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///store.db'
#db = SQLAlchemy(app)

app.config.from_object(__name__)
Session(app)


# function for generation of random string
def generate_random_string(stringLength=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(stringLength))


	    
	    
	    

@app.route("/")
def home():
	session['u_id'] = generate_random_string()
	return render_template("home.html")
    



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
			session['mytoken'] = r.json()['token']
			flash(f'Login realizado com sucesso para {form.username.data}!', 'success')
			return redirect(url_for('selectproject', mytoken=session['mytoken']))
		else:
			flash('Login não realizado. Verifique o usuário e a senha.', 'danger')
	return render_template('logininventsys.html', title='LoginInventsys', form=form)




@app.route("/selectproject", methods=['GET', 'POST'])
def selectproject():
	mytoken=session.get('mytoken')
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
	form.selecionaprojeto.choices = tulpa
	

	if form.validate_on_submit():	
		if projetos:
			session['project'] = str(form.selecionaprojeto.data)
			session['projectname'] = str(dict(form.selecionaprojeto.choices).get(form.selecionaprojeto.data))
			flash(f'Projeto '+session['projectname']+' selecionado com sucesso!', 'success')
			return redirect(url_for('selectcategory', mytoken=session['mytoken'], project=session['project']))
		else:
			flash('Projeto não pode ser selecionado. Tente novamente.', 'danger')



	return render_template('selectprojecto.html', title='SelectProject', mytoken=mytoken, form=form)




@app.route("/selectcategory", methods=['GET', 'POST'])
def selectcategory():
	
	mytoken=session.get('mytoken')
	payload = {}
	headers = {
    
  		'Account': 'stesa',
  		'Token': mytoken,
	}
	projectid = session.get('project')

	caturl = 'https://api.inventsys.com.br/v4/projects/'+projectid+'/categories'
	categorias = requests.request('GET', caturl, headers=headers, data=payload, allow_redirects=False)

	catvariavel=""
	variavelnome=""
	catlista=[]
	listanomes=[]
	for i in range(0,len(categorias.json()['categories'])):
	    cat=(categorias.json()['categories'][i]['id'])
	    nome=(categorias.json()['categories'][i]['name'])
	    catvariavel=(str(cat))
	    catlista.append(catvariavel)
	    variavelnome=(str(nome))
	    listanomes.append(variavelnome)
	tulpa = [(x, y) for x, y in zip(catlista, listanomes)]

	form = CategoryForm()
	form.selecionacategoria.choices = tulpa

	if form.validate_on_submit():	
		if categorias:
			session['category'] = str(form.selecionacategoria.data)
			session['categoryname'] = str(dict(form.selecionacategoria.choices).get(form.selecionacategoria.data))
			session['inicio']=form.inicio.data
			session['fim']=form.fim.data
			flash(f'Categoria '+session['categoryname']+' selecionado com sucesso!', 'success')
			return redirect(url_for('loginpostgis', mytoken=session['mytoken'], project=session['project'], category=session['category']))
		else:
			flash('Categoria não pode ser selecionada. Tente novamente.', 'danger')



	return render_template('selectcategory.html', title='SelectCategory', mytoken=mytoken, form=form)




@app.route("/loginpostgis", methods=['GET', 'POST'])
def loginpostgis():
	mytoken=session.get('mytoken')
	payload = {}
	headers = {
    
  		'Account': 'stesa',
  		'Token': mytoken,
	}
	page = 1
	registrosbruto = []
	projectid = session.get('project')
	categoryid = session.get('category')
	datainicio = session.get('inicio')
	datafim = session.get('fim')
	while True:
	    try:
	        url = 'https://api.inventsys.com.br/v4/projects/'+projectid+'/items?category='+categoryid+'&pagesize=1&page='+str(page)+'&since='+str(datainicio)
	        ativos = requests.request('GET', url, headers=headers, data=payload, allow_redirects=False)
	        
	        registrosbruto = registrosbruto + ativos.json()['items']
	    # ... put any other Exception you need to handle here
	    except IndexError:
	        break
	    else:
	        if len(ativos.json()['items'])==0:
	            break
	        else:
	            page += 1


	registros=[]
	for i in range(0,len(registrosbruto)):
	    ano=int(registrosbruto[i]['updated_at'][0:4])
	    mes=int(registrosbruto[i]['updated_at'][5:7])
	    dia=int(registrosbruto[i]['updated_at'][8:10])
	    dataobjeto = datetime.date(ano, mes, dia)
	    if dataobjeto<datafim:
	        registros.append(registrosbruto[i])
	
	ano=datafim.year
	mes=datafim.month
	if mes<10:
		dataref=str(ano)+'0'+str(mes)
	else:
		dataref=str(ano)+str(mes)
	session['dataref']=dataref

	form = LoginFormPostgis()
	if form.validate_on_submit():
		session['hostinput'] = str(form.hostinput.data)
		session['dbnameinput'] = str(form.dbnameinput.data)
		session['userinput'] = str(form.userinput.data)
		session['senhainput'] = str(form.senhainput.data)
		#Define our connection string
		conn_string = "host="+str(session.get('hostinput'))+" dbname="+str(session.get('dbnameinput'))+" user="+str(session.get('userinput'))+" password="+str(session.get('senhainput'))
		 
		 
		# get a connection, if a connect cannot be made an exception will be raised here
		conn = psycopg2.connect(conn_string)
		 
		# conn.cursor will return a cursor object, you can use this cursor to perform queries
		cur = conn.cursor()


		if conn:
			
			flash(f'Dados enviados com sucesso para {form.dbnameinput.data}!', 'success')

			projectid=session.get('project')
			categoryid=session.get('category')
			

			dropdbgenerica = """CREATE EXTENSION IF NOT EXISTS postgis;
			DROP TABLE IF EXISTS {}""" 

			nometabela=dataref+'_'+projectid+'_'+categoryid

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
			longitude real,
			geom geometry(Point, 4326)
			);""" 




			dbobracorrente = """CREATE EXTENSION IF NOT EXISTS postgis;
			DROP TABLE IF EXISTS {};
			CREATE UNLOGGED TABLE IF NOT EXISTS {}(
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
			natureza_obstrucao text,
			geom geometry(Point, 4326)
			);""" 


			dbobraespecial = """CREATE EXTENSION IF NOT EXISTS postgis;
			DROP TABLE IF EXISTS {};
			CREATE UNLOGGED TABLE IF NOT EXISTS {}(
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
			geom geometry(Point, 4326)
			);""" 


			dbarmadilhas = """CREATE EXTENSION IF NOT EXISTS postgis;
			DROP TABLE IF EXISTS {};
			CREATE UNLOGGED TABLE IF NOT EXISTS {}(
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
			gps_acc real,
			geom geometry(Point, 4326)
			);""" 
			    

			dbatropelamentos = """CREATE EXTENSION IF NOT EXISTS postgis;
			DROP TABLE IF EXISTS {};
			CREATE UNLOGGED TABLE IF NOT EXISTS {}(
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
			ponto_gps text,
			geom geometry(Point, 4326)
			);"""



			if categoryid=='20685':
			    cur.execute(sql.SQL(dbarmadilhas)
			                .format(sql.Identifier(nometabela), sql.Identifier(nometabela)))
			    tabelagerada=dataref+'_'+projectid+'_'+categoryid
			else:
			    if categoryid=='20686':
			        cur.execute(sql.SQL(dbatropelamentos)
			                .format(sql.Identifier(nometabela), sql.Identifier(nometabela)))
			        tabelagerada=dataref+'_'+projectid+'_'+categoryid
			    else:
			        if categoryid=='18278':
			            cur.execute(sql.SQL(dbobraespecial)
			                .format(sql.Identifier(nometabela), sql.Identifier(nometabela)))
			            tabelagerada=dataref+'_'+projectid+'_'+categoryid
			        else:
			            if categoryid=='18284':
			                cur.execute(sql.SQL(dbobracorrente)
			                .format(sql.Identifier(nometabela), sql.Identifier(nometabela)))
			                tabelagerada=dataref+'_'+projectid+'_'+categoryid
			            else:
			                cur.execute(sql.SQL(dropdbgenerica)
			                            .format(sql.Identifier(nometabela)))
			                cur.execute(sql.SQL(createdbgenerica)
			                            .format(sql.Identifier(nometabela)))
			                tabelagerada=dataref+'_'+projectid+'_'+categoryid

			conn.commit()

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
			            cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)").format(sql.Identifier(nometabela)), tuple(my_data))
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
			        cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)").format(sql.Identifier(nometabela)), tuple(my_data))
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
			        cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)").format(sql.Identifier(nometabela)), tuple(my_data))
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
			        cur.execute(sql.SQL("INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)").format(sql.Identifier(nometabela)), tuple(my_data))
			else:
			    print('.')
			    
			conn.commit()

			nomeindex=tabelagerada+'index'
			cur.execute(sql.SQL("UPDATE {} SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326); CREATE INDEX {} ON {} USING GIST(geom)").format(sql.Identifier(tabelagerada), sql.Identifier(nomeindex), sql.Identifier(tabelagerada)))
			    
			conn.commit()

			dbsegmentos = """DROP TABLE IF EXISTS {};
			CREATE UNLOGGED TABLE IF NOT EXISTS {}(
			nome TEXT PRIMARY KEY,
			geom geometry(MultiPolygon, 4326)
			);""" 
			segmentnome="egrfauna_segmentos"
			cur.execute(sql.SQL(dbsegmentos).format(sql.Identifier(segmentnome), sql.Identifier(segmentnome)))
			conn.commit()

			segmentos=requests.get('https://raw.githubusercontent.com/guilhermeiablo/inventsys2infoambiente/master/dados/ERS_segmentos_rodoviarios.geojson')


			for feature in segmentos.json()['features']:
			    geom = (json.dumps(feature['geometry']))
			    nome=feature['properties']['nome']
			    cur.execute(sql.SQL("INSERT INTO {} (nome, geom) VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));").format(sql.Identifier(segmentnome)), (nome, geom))
			cur.execute(sql.SQL("CREATE INDEX sp_index_segmentos ON {} USING GIST(geom)").format(sql.Identifier(segmentnome)))

			conn.commit()



			intersecta = '''DROP TABLE IF EXISTS {nome0}; SELECT {nome1}.*, {nome2}.nome INTO {nome0} FROM {nome2} INNER JOIN {nome1} ON ST_Intersects({nome2}.geom, {nome1}.geom) AND {nome2}.nome=%s;'''

			for feature in segmentos.json()['features']:
			    nomedosegmento=feature['properties']['nome']
			    if projectid=='10762':
			        nomecompleto=str(feature['properties']['nome']+'_PMF_'+tabelagerada)
			    else:
			        nomecompleto=str(feature['properties']['nome']+'_'+tabelagerada)
			    cur.execute(sql.SQL(intersecta)
			                .format(nome0=sql.Identifier(nomecompleto),nome1=sql.Identifier(tabelagerada),nome2=sql.Identifier(segmentnome)),[nomedosegmento,])


			conn.commit()
			session['tabelagerada']=str(tabelagerada)



			return redirect(url_for('logingeoserver', mytoken=session['mytoken'], project=session['project'], category=session['category']))
		else:
			flash('Erro ao conectar a base de dados. Tente novamente.', 'danger')
	return render_template('loginpostgis.html', title='LoginPostgis', form=form, mytoken=mytoken, project=session['project'], category=session['category'])




@app.route("/logingeoserver", methods=['GET', 'POST'])
def logingeoserver():
	form = LoginFormGeoserver()
	mytoken=session.get('mytoken')
	projectid=session.get('project')
	categoryid=session.get('category')
	segmentos=requests.get('https://raw.githubusercontent.com/guilhermeiablo/inventsys2infoambiente/master/dados/ERS_segmentos_rodoviarios.geojson')
	tabelagerada=session.get('tabelagerada')


	if form.validate_on_submit():
		urlgeoserver = str(form.urlgeoserver.data)
		usrgeoserver = str(form.usrgeoserver.data)
		pwdgeoserver = str(form.pwdgeoserver.data)
		workspace = str(form.workspace.data)
		datastore = str(form.datastore.data)


		cat = Catalog(urlgeoserver, username=usrgeoserver, password=pwdgeoserver)
		cite = cat.get_workspace(workspace)
		ds = cat.get_store(datastore, workspace)


		ds.connection_parameters.update(host=session.get('hostinput'), port='5432', database=session.get('dbnameinput'), user=session.get('userinput'), passwd=session.get('pwdgeoserver'), dbtype='postgis', schema='public')
		cat.save(ds)


		if cat:
			
			flash(f'Dados enviados com sucesso para {form.workspace.data}!', 'success')


			for feature in segmentos.json()['features']:
			    if projectid=='10762':
			        nomedolayer=str(str(feature['properties']['nome'])+'_PMF_'+str(tabelagerada))
			    else:
			        nomedolayer=str(str(feature['properties']['nome'])+'_'+str(tabelagerada))
			        
			    while True:
			        try:
			            ft = cat.publish_featuretype(nomedolayer, ds, 'EPSG:4326', srs='EPSG:4326')

			        except:
			            # for handle unknown exception
			            # define your parameters
			            urldatastore = urlgeoserver+'reset'
			            headersdatastore = {'Content-Type': 'text/xml'}
			            authdatastore = (usrgeoserver, pwdgeoserver)
			            r = requests.post(urldatastore, headers=headersdatastore, auth=authdatastore)
			            break

			return redirect(url_for('logininfoambiente', mytoken=session['mytoken'], project=session['project'], category=session['category']))
		else:
			flash('Erro ao conectar ao servidor. Tente novamente.', 'danger')



	return render_template("logingeoserver.html", title='LoginGeoserver', form=form, mytoken=mytoken, project=session['project'], category=session['category'])

@app.route("/logininfoambiente", methods=['GET', 'POST'])
def logininfoambiente():
	form = LoginFormInfoambiente()
	mytoken=session.get('mytoken')
	projectid=session.get('project')
	categoryid=session.get('category')
	segmentos=requests.get('https://raw.githubusercontent.com/guilhermeiablo/inventsys2infoambiente/master/dados/ERS_segmentos_rodoviarios.geojson')
	tabelagerada=session.get('tabelagerada')
	if form.validate_on_submit():
		usrinfoambiente = str(form.usrinfoambiente.data)
		pwdinfoambiente = str(form.pwdinfoambiente.data)


		URL = 'http://www.infoambiente.stesa.com.br/egr'

		rsession = requests.session()

		front = rsession.get(URL)
		csrf_token = re.findall(r'<input type="hidden" name="_token" value="(.*)"', 
		front.text)[0]
		cookies = rsession.cookies


		payload = {
		    'usuario': usrinfoambiente,
		    'password': pwdinfoambiente,
		    'projeto': 'egr',
		    'X-XSRF-TOKEN': csrf_token,
		    '_token': csrf_token
		}

		r = requests.request('POST', 'http://www.infoambiente.stesa.com.br/login', data=payload, cookies=cookies)
		cookies = r.cookies
		egr = requests.request('GET', 'http://www.infoambiente.stesa.com.br/egr', data=payload, cookies=cookies)
		chamada = requests.request('GET', 'http://www.infoambiente.stesa.com.br/tree/41', data=payload, cookies=cookies)
		
		quarentaeum = json.loads(chamada.text)
		#algo = json.dumps(quarentaeum.json())
		


		if egr:

			for i in range(0,len(quarentaeum)):
			    if quarentaeum[i]['text']=='Núcleo 01':
			        nodenucleo1=quarentaeum[i]['id']
			        session['nodenucleo1']=nodenucleo1
			    if quarentaeum[i]['text']=='Núcleo 02':
			        nodenucleo2=quarentaeum[i]['id']
			        session['nodenucleo2']=nodenucleo2
			    if quarentaeum[i]['text']=='Núcleo 03':
			        nodenucleo3=quarentaeum[i]['id']
			        session['nodenucleo3']=nodenucleo3

			for i in range(0,len(quarentaeum)):
			    if quarentaeum[i]['parent']==nodenucleo1:
			        if quarentaeum[i]['text']=='Programas Ambientais':
			            nodeprogramas1=quarentaeum[i]['id']
			            session['nodeprogramas1']=nodeprogramas1
			    if quarentaeum[i]['parent']==nodenucleo2:
			        if quarentaeum[i]['text']=='Programas Ambientais':
			            nodeprogramas2=quarentaeum[i]['id']
			            session['nodeprogramas2']=nodeprogramas2
			    if quarentaeum[i]['parent']==nodenucleo3:
			        if quarentaeum[i]['text']=='Programas Ambientais':
			            nodeprogramas3=quarentaeum[i]['id']
			            session['nodeprogramas3']=nodeprogramas3

			programasambientais=[]            
			for i in range(0,len(quarentaeum)):
			    if quarentaeum[i]['parent']==nodeprogramas1:
			        programasambientais.append(quarentaeum[i]['text'])

			session['programasambientais']=programasambientais
			session['quarentaeum']=quarentaeum
			session['cookies']=cookies
			session['csrf_token']=csrf_token
			session['infoambientepayload']=payload

			
			flash(f'Login realizado com sucesso para o usuário {form.usrinfoambiente.data}!', 'success')

			return redirect(url_for('selectprograma', mytoken=session['mytoken'], project=session['project'], category=session['category']))
		else:
			flash('Usuário ou senha inválidos. Tente novamente.', 'danger')



	return render_template("logininfoambiente.html", title='LoginInfoambiente', form=form, mytoken=mytoken, project=session['project'], category=session['category'])



@app.route("/selectprograma", methods=['GET', 'POST'])
def selectprograma():
	form = ProgramaForm()
	form.selecionaprograma.choices = sorted(session.get('programasambientais'))
	mytoken=session.get('mytoken')
	projectid=session.get('project')
	categoryid=session.get('category')
	segmentos=requests.get('https://raw.githubusercontent.com/guilhermeiablo/inventsys2infoambiente/master/dados/ERS_segmentos_rodoviarios.geojson')
	tabelagerada=session.get('tabelagerada')
	payload=session.get('infoambientepayload')
	csrf_token=session.get('csrf_token')
	programasambientais=session.get('programasambientais')
	quarentaeum=session.get('quarentaeum')
	cookies=session.get('cookies')
	nodenucleo1=session.get('nodenucleo1')
	nodenucleo2=session.get('nodenucleo2')
	nodenucleo3=session.get('nodenucleo3')
	nodeprogramas1=session.get('nodeprogramas1')
	nodeprogramas2=session.get('nodeprogramas2')
	nodeprogramas3=session.get('nodeprogramas3')
	
	if form.validate_on_submit():
		
		programaid=str(form.selecionaprograma.data)

		for i in range(0,len(quarentaeum)):
		    if quarentaeum[i]['parent']==nodeprogramas1:
		        if quarentaeum[i]['text']==programaid:
		            nodeprogramaescolhido1=quarentaeum[i]['id']
		    if quarentaeum[i]['parent']==nodeprogramas2:
		        if quarentaeum[i]['text']==programaid:
		            nodeprogramaescolhido2=quarentaeum[i]['id']
		    if quarentaeum[i]['parent']==nodeprogramas3:
		        if quarentaeum[i]['text']==programaid:
		            nodeprogramaescolhido3=quarentaeum[i]['id']

		for i in range(0,len(quarentaeum)):
		    if quarentaeum[i]['parent']==nodeprogramaescolhido1:
		        if quarentaeum[i]['text']=='ERS-115':
		            noders115=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-239':
		            noders239=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-474':
		            noders474=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-020':
		            noders020=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-235':
		            noders235=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-466':
		            noders466=quarentaeum[i]['id']
		    if quarentaeum[i]['parent']==nodeprogramaescolhido2:
		        if quarentaeum[i]['text']=='ERS-129':
		            noders129=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-130':
		            noders130=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-135':
		            noders135=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='RSC-287 Trecho 1 e 2':
		            noders287t1e2=quarentaeum[i]['id']
		    if quarentaeum[i]['parent']==nodeprogramaescolhido3:
		        if quarentaeum[i]['text']=='ERS-240':
		            noders240=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-122':
		            noders122=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-784':
		            noders784=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-040':
		            noders040=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='ERS-128':
		            noders128=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='RSC-453':
		            noders453=quarentaeum[i]['id']
		        if quarentaeum[i]['text']=='RSC-287 Trecho 3':
		            noders287t3=quarentaeum[i]['id']

		#Adicionar camada
		for feature in segmentos.json()['features']:
		    if projectid=='10762':
		        nomedolayer=str(feature['properties']['nome']+'_PMF_'+tabelagerada)
		    else:
		        nomedolayer=str(feature['properties']['nome']+'_'+tabelagerada)
		    if 'ERS115' in nomedolayer:
		        parentecamada = noders115[5:9]
		    if 'ERS239' in nomedolayer:
		        parentecamada = noders239[5:9]
		    if 'ERS474' in nomedolayer:
		        parentecamada = noders474[5:9]
		    if 'ERS020' in nomedolayer:
		        parentecamada = noders020[5:9]
		    if 'ERS235' in nomedolayer:
		        parentecamada = noders235[5:9]
		    if 'ERS466' in nomedolayer:
		        parentecamada = noders466[5:9]
		    if 'ERS129' in nomedolayer:
		        parentecamada = noders129[5:9]
		    if 'ERS130' in nomedolayer:
		        parentecamada = noders130[5:9]
		    if 'ERS135' in nomedolayer:
		        parentecamada = noders135[5:9]
		    if 'RSC287_P' in nomedolayer:
		        parentecamada = noders287t1e2[5:9]
		    if 'RSC287_T' in nomedolayer:
		        parentecamada = noders287t3[5:9]
		    if 'ERS240' in nomedolayer:
		        parentecamada = noders240[5:9]
		    if 'ERS122' in nomedolayer:
		        parentecamada = noders122[5:9]
		    if 'ERS784' in nomedolayer:
		        parentecamada = noders784[5:9]
		    if 'ERS040' in nomedolayer:
		        parentecamada = noders040[5:9]
		    if 'ERS128' in nomedolayer:
		        parentecamada = noders128[5:9]
		    if 'RSC453' in nomedolayer:
		        parentecamada = noders453[5:9]
		    
		    if not str(form.novonome.data):
			    payloadcamadas = {
			        'projetoCamada': '41',
			        'parenteCamada': parentecamada,
			        'nomeCamada': nomedolayer,
			        'nomeOriginalCamada': nomedolayer,
			        'ativaCamada': '0',
			        'X-XSRF-TOKEN': csrf_token,
			        '_token': csrf_token
			    }
		    else:
			    payloadcamadas = {
			        'projetoCamada': '41',
			        'parenteCamada': parentecamada,
			        'nomeCamada': str(form.novonome.data),
			        'nomeOriginalCamada': nomedolayer,
			        'ativaCamada': '0',
			        'X-XSRF-TOKEN': csrf_token,
			        '_token': csrf_token
			    }
		    
		    while True:
		        try:
		            uppa = requests.request('POST', 'http://www.infoambiente.stesa.com.br/camadas', data=payloadcamadas, cookies=cookies)
		            ok='ok'
		            break
		        except:
		            quarentaeum = requests.request('GET', 'http://www.infoambiente.stesa.com.br/tree/41', data=payload, cookies=cookies)
		            ok='ok'
		            break
		if ok=='ok':
			flash(f'Dados enviados com sucesso para o Infoambiente sob o programa {form.selecionaprograma.data}!', 'success')

			return redirect(url_for('success', mytoken=session['mytoken'], project=session['project'], category=session['category']))
		else:
			flash('Erro ao enviar os dados. Tente novamente.', 'danger')



	return render_template("selectprograma.html", title='SelectPrograma', form=form, mytoken=mytoken, project=session['project'], category=session['category'])




@app.route("/success")
def success():

	return render_template("success.html", mytoken=session['mytoken'], projectname=session['projectname'], categoryname=session['categoryname'])






    
if __name__ == "__main__":
    app.run(debug=True)