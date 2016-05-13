def get_hosts():
	hosts={"ungrouped":[]}
	with open('/etc/ansible/hosts', 'r') as f:
		cur_group="ungrouped"
		for line in f.readlines():
			line=line.strip().split('#')[0]
			if line=="":
				continue
			if line[0]=='[' and line[len(line)-1]==']':
				cur_group=line[1:len(line)-1]
				hosts[cur_group]=[]
				continue
			hosts[cur_group].append(line)
	return(hosts)

def set_hosts(hosts):
	str_host=""
	try:
		for host in hosts['ungrouped']:
			str_host+= "%s\n" % host
		hosts.pop('ungrouped')
	except:
		pass
	for group in hosts:
		str_host+= "[%s]\n" % group
		for host in hosts[group]:
			str_host+= "%s\n" % host

	with open('/etc/ansible/hosts','w') as f:
		f.write(str_host)

def remove_host(group, host):
	hosts= get_hosts()
	hosts[group].remove(host)
	set_hosts(hosts)

def add_host(group, host):
	hosts= get_hosts()
	hosts[group].append(host)
	print(hosts)
	set_hosts(hosts)

def add_group(group):
	hosts= get_hosts()
	hosts[group]=[]
	set_hosts(hosts)

def remove_group(group):
	hosts= get_hosts()
	hosts.pop(group)
	set_hosts(hosts)
