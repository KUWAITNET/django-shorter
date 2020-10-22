user = ''
password = ''
host = '127.0.0.1'
database = ''
raise_on_warnings = True

config = {
    'user': user,
    'password': password,
    'host': host,
    'database': database,
    'raise_on_warnings': raise_on_warnings
}

def set_configs(user=None, password=None, database=None):
    config['user'] = user
    config['password'] = password
    config['database'] = database



