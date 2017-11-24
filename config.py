import os

basedir = os.path.abspath(os.path.dirname(__file__))


#SQL ALCHEMY

#dir stuff for the db scripts
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SQLALCHEMY_TRACK_MODIFICATIONS = False #to remove that annoying compilation message

#CSRF PROTECTION
WTF_CSRF_ENABLED = True;
SECRET_KEY = 'ajja'


#login credentials
os.environ['MAIL_USERNAME'] = "voitheiaemail@gmail.com"
os.environ['MAIL_PASSWORD'] = "paytmkaro69"


# email server with settings for a gmail account as the sending server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['voitheiaemail@gmail.com']

# pagination
POSTS_PER_PAGE = 3


#DATABASE PROFILING

SQLALCHEMY_RECORD_QUERIES = True

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

#CAPTCHA FOR REGISTER
RECAPTCHA_PUBLIC_KEY = '6LflGjoUAAAAAKY6rUlaQwFbXQ3jeiDXx3jaTR3b'
RECAPTCHA_PRIVATE_KEY = '6LflGjoUAAAAAJ--_sQU_vNXBhmlTLXTci84AURW'