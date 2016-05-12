def get_hosts():
	hosts={"default":[]}
	with open('/etc/ansible/hosts', 'r') as f:
		cur_group="default"
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
