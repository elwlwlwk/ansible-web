from flask import Flask, render_template, session, url_for, redirect, request
import user
import copy
app= Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
	import configparser
	import os
	if 'passwd' not in os.listdir():
		if request.method== 'POST':
			user_name= request.form['user_name']
			passwd= request.form['passwd']
			user.new_user(user_name, passwd)
		else:
			return render_template('add_user.html', new_user=True)
		return redirect(url_for('index'))
	if 'logged_in' in session and session['logged_in']== True:
		if request.method== 'POST':
			config= configparser.ConfigParser()
			config.read('/etc/ansible/ansible.cfg')
			for form_key in request.form:
				section, key= form_key.split("@")
				config[section][key]= request.form[form_key]
				with open('/etc/ansible/ansible.cfg', 'w') as configfile:
					config.write(configfile)
			return redirect(url_for('index'))
		else:
			config= configparser.ConfigParser()
			config.read('/etc/ansible/ansible.cfg')
			config['defaults']['ansible_managed']=''
			config['defaults'].pop('ansible_managed')
			return render_template('index.html', config= config)
	else:
		return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method== 'POST':
		username= request.form['username']
		passwd= request.form['passwd']
		if user.login_validator(username, passwd):
			session['username']= username
			session['logged_in']= True
		else:
			return render_template('index.html', login_fail=True)
	return redirect(url_for('index'))

@app.route("/logout", methods=['GET'])
def logout():
	session.pop('username', None)
	session.pop('logged_in', None)
	return redirect(url_for('index'))

@app.route("/change_passwd", methods=['GET', 'POST'])
def change_passwd():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	if request.method== 'POST':
		user.change_passwd(session['username'], request.form['passwd'])
		logout()

	return render_template('change_passwd.html')

@app.route("/hosts", methods=['GET'])
def hosts():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	from hosts import get_hosts
	hosts=get_hosts()
	return render_template('hosts.html', hosts=hosts)

@app.route("/remove_host", methods=['GET', 'POST'])
def remove_host():
	if request.method=='POST':
		import hosts
		if 'logged_in' not in session or session['logged_in']!= True:
			host= request.environ['REMOTE_ADDR']
		else:
			host= request.form['host']

		group= request.form['group']
		hosts.remove_host(group, host)

	return redirect(url_for('hosts'))

@app.route("/add_host", methods=['GET', 'POST'])
def add_host():
	if request.method=='POST':
		import hosts
		if 'logged_in' not in session or session['logged_in']!= True:
			host= request.environ['REMOTE_ADDR']
		else:
			host= request.form['host']

		group= request.form['group']
		hosts.add_host(group, host)

	return redirect(url_for('hosts'))

@app.route("/add_group", methods=['GET', 'POST'])
def add_group():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	if request.method=='POST':
		import hosts
		group= request.form['group']
		hosts.add_group(group)

	return redirect(url_for('hosts'))

@app.route("/remove_group", methods=['GET', 'POST'])
def remove_group():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	if request.method=='POST':
		import hosts
		group= request.form['group']
		hosts.remove_group(group)

	return redirect(url_for('hosts'))

@app.route("/playbooks")
def playbooks():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	import os
	playbooks= []
	for f in os.listdir('playbooks'):
		if 'yml' in f:
			playbooks.append(f)
	playbooks.sort()
	return render_template('playbooks.html', playbooks= playbooks)

@app.route("/playbook")
def playbook():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	playbook= request.args['playbook']
	with open('playbooks/%s' % playbook, 'r') as f:
		playscript= f.read()

	from hosts import get_hosts
	hosts=get_hosts()

	from jinja2 import Environment, PackageLoader, meta
	env= Environment(loader= PackageLoader('playbooks',''))
	template_source= env.loader.get_source(env, playbook)[0]
	parsed_content= env.parse(template_source)
	extra_vars= meta.find_undeclared_variables(parsed_content)

	return render_template('playbook.html', playbook= playbook, playscript= playscript, hosts=hosts, extra_vars= extra_vars)

@app.route("/play", methods=['GET', 'POST'])
def play():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	if request.method== 'POST':
		import os, datetime
		playbook= request.form['playbook']
		variables= ''
		for variable in request.form:
			if variable== 'playbook':
				continue
			variables+='%s=%s ' % (variable, request.form[variable])
		if playbook not in os.listdir('logs'):
			os.system('mkdir logs/%s' % playbook)
		os.system('nohup ansible-playbook playbooks/%s --extra-vars "%s" > logs/%s/%s_%s &' % (playbook, variables, playbook, playbook, str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))))

	return redirect(url_for('playbooks'))

@app.route("/logs")
def logs():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	import os

	logs=[]
	for playbook in os.listdir('logs'):
		log= os.listdir('logs/%s' % playbook)
		logs+=log
	logs.sort(key=(lambda x:x[-14:]), reverse=True)
	return render_template('logs.html', logs=logs)

@app.route("/log")
def log():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))
	logname= request.args['log']
	with open('logs/%s' % logname, 'r') as f:
		log= f.read()
	return render_template('log.html', logname=logname.split("/")[1], log=log)

@app.route("/log_del")
def log_del():
	if 'logged_in' not in session or session['logged_in']!= True:
		return redirect(url_for('index'))

	import os
	os.remove('logs/%s' % request.args['log'])

	return redirect(url_for('logs'))

@app.route("/get_pubkey")
def get_pubkey():
	import os
	with open('%s/.ssh/id_rsa.pub' % os.getenv("HOME"), 'r') as f:
		pub_key= f.read()
	return pub_key;

if __name__== "__main__":
	import config
	app.debug= config.SERVER_DEBUG
	app.secret_key= 'ansible-web-secret-key'
	app.run(host=config.SERVER_HOST, port=config.SERVER_PORT)
