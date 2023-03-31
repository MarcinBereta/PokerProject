import os
from pymongo import MongoClient
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
cluster = "mongodb+srv://Mardorus:PokerAGH@poker.gmn3mgg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cluster)
from Auth import AuthHandler


@app.route('/')
def index():
    return 'Hello World!'

@app.route('/images/<path:path>')
def send_image(path):
    img_dir = './images'
    img_list = os.listdir(img_dir)
    img_path = os.path.join(img_dir, path)
    return send_file(img_path, mimetype='image/png')
@app.route('/login')
def login():
    return "login"


@app.route('/login', methods=['POST'])
def handle_login():
    loginData = request.form
    return loginHandler.login(loginData)


@app.route('/register', methods=['POST'])
def handle_register():
    registerData = request.form
    if 'file' not in request.files:
        return loginHandler.register(registerData, None)
    else:
        file = request.files['file']
        file.save(os.path.join('./images/', file.filename))
        return loginHandler.register(registerData, file.filename)


@app.route('/forgot_password', methods=['POST'])
def handle_forgot_password():
    forgotPasswordData = request.form
    return loginHandler.forgot_password(forgotPasswordData)

@app.route('/save_score', methods=['POST'])
def handle_save_score():
    scoreData = request.form
    return loginHandler.save_score(scoreData)

if __name__ == "__main__":
    db = client["poker"]
    loginHandler = AuthHandler(db)
    app.run(debug=True, port=5000, host='127.0.0.1')
