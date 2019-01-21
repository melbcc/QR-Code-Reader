from flask import render_template, send_from_directory

from .base import app


@app.route('/', methods=['GET'])
def render_root():
    return render_template('root.html')

@app.route('/scanner', methods=['GET'])
def render_scanner():
    return render_template('scanner.html')

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
