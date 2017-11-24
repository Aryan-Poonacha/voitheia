from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

#email imports
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD


#///////////// MAIN CLASS OBJECTS /////////////////////////

app = Flask(__name__) #creates an object of the Flask class called app

app.config.from_object('config') #this sets that the config file for all flask extensions is config.py

db = SQLAlchemy(app) #the object of the sqlalchemy class

mail = Mail(app) #the object of the flask_email class


lm = LoginManager() #the login manager object
lm.init_app(app) #initialise the object of the login manager
lm.login_view = 'login' #allows flask to see which page to redirect to for url_for('next')

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"]) #an object of the token generator class that will be used for the same



#///////////////// DEBUGGING / PRODUCTION ///////////////?????//////////

#running this script places the server in production mode, appropriate for deployment
#app.run(debug = False)


#email error message sending automation
'''
if not app.debug: #works only when in production mode, not debugging mod e
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

'''

#file error message posting automation. Stores all error related stuff in the tmp dir in a file called erros.log
'''
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/errors.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')
'''




#///////////////// MISC /////////////////////////////

from app import views, models #refers to app the directory, which is now a package. views is app.routes, models is database stuff