from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flask HTML Example</title>
    </head>
    <body>
        <h1>Hello, world!</h1>
        <p>This is a paragraph.</p>
    </body>
    </html>
    """
    return html_code
