from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    with open('templates/index.html', 'r') as file:
        html_content = file.read()
    return html_content
