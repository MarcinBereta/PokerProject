import os
from pymongo import MongoClient
from flask import Flask, request, send_file
from PIL import Image
from auth import AuthHandler

app = Flask(__name__)
cluster =""
client = MongoClient(cluster)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/images/<path:path>')
def send_image(path):
    img_dir = './images'
    os.listdir(img_dir)
    img_path = os.path.join(img_dir, path)
    return send_file(img_path, mimetype='image/png')


@app.route('/login')
def login():
    return "login"


@app.route('/login', methods=['POST'])
def handle_login():
    login_data = request.form
    return loginHandler.login(login_data)


@app.route('/register', methods=['POST'])
def handle_register():
    register_data = request.form
    if 'file' not in request.files:
        return loginHandler.register(register_data, None)
    else:
        file = request.files['file']
        if file.filename == '':
            return loginHandler.register(register_data, None)
        if len(file.filename.split(' ')) > 1:
            return loginHandler.register(register_data, None)
        file.save(os.path.join('./images/', file.filename))
        image = Image.open(os.path.join('./images/', file.filename))
        image.resize((100, 100), Image.LANCZOS)
        print("resized")
        image.save(file.filename)
        return loginHandler.register(register_data, file.filename)


@app.route('/forgot_password', methods=['POST'])
def handle_forgot_password():
    forgot_password_data = request.form
    return loginHandler.forgot_password(forgot_password_data)


@app.route('/verify_code', methods=['POST'])
def verify_code():
    forgot_password_data = request.form
    return loginHandler.verify_code(forgot_password_data)


@app.route('/change_password', methods=['POST'])
def change_password():
    forgot_password_data = request.form
    return loginHandler.change_password(forgot_password_data)


@app.route('/save_score', methods=['POST'])
def handle_save_score():
    scoreData = request.form
    return loginHandler.save_score(scoreData)


@app.route('/get_leaderboard/<path:username>', methods=['GET'])
def get_leaderboard(username):
    return loginHandler.get_leaderboard(username)


@app.route('/get_profile/<path:username>', methods=['GET'])
def handle_get_profile(username):
    return loginHandler.get_user_scores(username)


@app.route('/update_user_data', methods=['POST'])
def handle_user_update():
    update_data = request.form
    if 'file' not in request.files:
        return loginHandler.update_user_data(update_data, None)
    else:
        file = request.files['file']
        if file.filename == '':
            return loginHandler.update_user_data(update_data, None)
        if len(file.filename.split(' ')) > 1:
            return loginHandler.update_user_data(update_data, None)
        file.save(os.path.join('./images/', file.filename))
        image = Image.open(os.path.join('./images/', file.filename))
        image.resize((100, 100), Image.LANCZOS)
        image.save(file.filename)
        return loginHandler.update_user_data(update_data, file.filename)


if __name__ == "__main__":
    db = client["poker"]
    loginHandler = AuthHandler(db)
    app.run(debug=True, port=5000, host='127.0.0.1')
