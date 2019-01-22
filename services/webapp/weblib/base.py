from flask import Flask

app = Flask(__name__)

# Database Session
session = None  # must be set before flask app start

def set_session(ses):
    globals()['session'] = ses
