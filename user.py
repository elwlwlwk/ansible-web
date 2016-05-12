import hashlib
valid_hashed_passwd=""

def login_validator(username, passwd):
	with open('passwd', 'r') as f:	
		valid_hashed_passwd= f.read().strip()
	with open('user', 'r') as f:
		valid_username= f.read().strip()
	hashed_passwd= hashlib.sha224(hashlib.sha224(passwd.encode()).hexdigest().encode()).hexdigest()

	if username== valid_username and valid_hashed_passwd== hashed_passwd:
		return True
	else:
		return False

def change_passwd(username, passwd):
	with open('user', 'r') as f:
		valid_username= f.read().strip()
	if valid_username != username:
		return False
	valid_hashed_passwd= hashlib.sha224(hashlib.sha224(passwd.encode()).hexdigest().encode()).hexdigest()
	with open('passwd', 'w') as f:
		f.write(valid_hashed_passwd)
		f.close()
	return True
