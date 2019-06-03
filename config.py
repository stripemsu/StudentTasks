#change DEBUG to false for production
DEBUG = True

SECURITY_USER_IDENTITY_ATTRIBUTES = 'login'
SQLALCHEMY_TRACK_MODIFICATIONS = False;
#Dev db
SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlite:///database.sqlite'

#Random key, generate yours
WTF_CSRF_SECRET_KEY = 'Secret key' 

#please update to your ldap directory
LDAP_PROVIDER_URL = 'ldaps://localhost'

#this user will be first admin in your system,
#however, autentification will be done over ldap
FIRST_ADMIN_USER = 'Superadmin'

#Fix path for production
IMAGE_FOLDER = './Images'
