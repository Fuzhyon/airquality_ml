from flask import Flask
app = Flask(__name__)
@app.route('/index')
def index():
    return 'Hello world'
if __name__ == '__main__':
    app.run(debug=True, port=1024, host='0.0.0.0')
