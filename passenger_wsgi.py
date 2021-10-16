import sys, os
INTERP = os.path.join(os.environ['HOME'], 'pythonenv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

# HELLO WORLD WEBSERVER TEST
#from flask import Flask
#application = Flask(__name__)

#@application.route('/')
#def index():
#    return 'Hello from Passenger'

# PRODUCTION 
sys.path.append(os.getcwd())
import flaskapp
application = flaskapp.create_app()
