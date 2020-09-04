from flask import Flask, Blueprint, render_template, url_for, flash, redirect, request, jsonify, session
from flask_session import Session
#from flask_sqlalchemy import SQLAlchemy
from getpass import getpass
import random , string
import requests
import json
from forms import LoginFormInventsys, ProjectForm, CategoryForm, LoginFormPostgis
import psycopg2
from psycopg2 import sql

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
			flash(f'Projeto {form.selecionaprojeto.data} selecionado com sucesso!', 'success')
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
			flash(f'Categoria {form.selecionacategoria.data} selecionado com sucesso!', 'success')
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
	registros = []
	projectid = session.get('project')
	categoryid = session.get('category')
	while True:
	    try:
	        url = 'https://api.inventsys.com.br/v4/projects/'+projectid+'/items?category='+categoryid+'&pagesize=1&page='+str(page)
	        ativos = requests.request('GET', url, headers=headers, data=payload, allow_redirects=False)
	        
	        registros = registros + ativos.json()['items']
	        
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

			nometabela=projectid+'_'+categoryid

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
			    tabelagerada=projectid+'_'+categoryid
			else:
			    if categoryid=='20686':
			        cur.execute(sql.SQL(dbatropelamentos)
			                .format(sql.Identifier(nometabela), sql.Identifier(nometabela)))
			        tabelagerada=projectid+'_'+categoryid
			    else:
			        if categoryid=='18278':
			            cur.execute(sql.SQL(dbobraespecial)
			                .format(sql.Identifier(nometabela), sql.Identifier(nometabela)))
			            tabelagerada=projectid+'_'+categoryid
			        else:
			            if categoryid=='18284':
			                cur.execute(sql.SQL(dbobracorrente)
			                .format(sql.Identifier(nometabela), sql.Identifier(nometabela)))
			                tabelagerada=projectid+'_'+categoryid
			            else:
			                cur.execute(sql.SQL(dropdbgenerica)
			                            .format(sql.Identifier(nometabela)))
			                cur.execute(sql.SQL(createdbgenerica)
			                            .format(sql.Identifier(nometabela)))
			                tabelagerada=projectid+'_'+categoryid

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



			return redirect(url_for('logingeoserver', mytoken=session['mytoken'], project=session['project'], category=session['category']))
		else:
			flash('Erro ao conectar a base de dados. Tente novamente.', 'danger')
	return render_template('loginpostgis.html', title='LoginPostgis', form=form, mytoken=mytoken, project=session['project'], category=session['category'])




@app.route("/logingeoserver")
def logingeoserver():
	
	    











	return render_template("logingeoserver.html")








    
if __name__ == "__main__":
    app.run(debug=True)