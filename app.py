from flask import Flask, request, redirect, url_for
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_pymongo import PyMongo
# from .credentials_file import credentials, settings
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash # Para criptografar a senha
from flask import jsonify, Flask, request
import requests

app = Flask(__name__)
# app.config["MONGO_URI"] = f"mongodb+srv://{credentials['user_mongo']}:{credentials['password_mongo']}@{settings['host']}/{settings['database']}?retryWrites=true&w=majority"
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@projagil.d9zuddb.mongodb.net/db_projeto"
mongo = PyMongo(app)

collection_usuarios = mongo.db.Usuarios
collection_mensagens = mongo.db.Mensagens
collection_remedios = mongo.db.Remedios

url_base = 'http://127.0.0.1:5000'

@app.route('/login', methods=['GET', 'POST'])
def login():
    request_data = request.json

    if request.method == 'POST':

        usuario = request_data.get('username')
        senha = request_data.get('password')

        if usuario is None:
            return jsonify("Campo de usuário não preenchido."), 400
        
        if senha is None:
            return jsonify("Campo da senha não preenchido."), 400

        user = collection_usuarios.find_one({"username": usuario, "password": senha})
        
        if user:
            return redirect(url_for('home'))
        else:
            return "Nome de usuário e/ou senha inválido(s)"

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_usuario():
    # return None
    request_data = request.json

    if request.method == 'POST':

        usuario = request_data.get('username')
        email = request_data.get('email')
        senha = request_data.get('password')
        
        already_exist = collection_usuarios.find_one({"email": email})

        if already_exist:
            return "Esse e-mail já está sendo utilizado."
        
        elif usuario is None or email is None or senha is None:
            return jsonify("Os campos não foram preenchidos por completo."), 400
     
        else:
            novo_usuario = {"username": usuario, "email": email, "password": senha}
            collection_usuarios.insert_one(novo_usuario)
            return redirect(url_for('login'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        message = request.form['message']
        if message:
            collection_mensagens.insert_one({'message': message})
            return "Mensagem enviada com sucesso", 200
        return "Mensagem não enviada", 400

def send_message_to_server(message):
    response = requests.post(f'{url_base}/send_message', data={'message': message})
    if response.status_code == 200:
        return True
    else:
        return False

@app.route('/get_messages', methods=['GET'])
def get_messages():
    if request.method == 'GET':
        messages = list(collection_mensagens.find())
        return jsonify(messages)
    
def get_messages_from_server():
    response = requests.get(f'{url_base}/get_messages')
    if response.status_code == 200:
        return response.json()
    else:
        return []
    
@app.route('/remedios', methods=['GET', 'POST'])
def remedios():
    data = request.json
    if request.method == 'POST':

        remedio = data.get('remedio')
        frequencia = data.get('frequencia')
        horario = data.get('horario')

        if remedio is None:
            return jsonify("Remédio não preenchido"), 400
        
        if frequencia is None:
            return jsonify("Frequência não especificada"), 400
        
        novo_remedio = {"remedio": remedio, "frequencia": frequencia, "horario": horario}
        collection_remedios.insert_one(novo_remedio)

    if request.method == 'GET':
        remedios = collection_remedios.find()
        return jsonify(remedios)

if __name__ == '__main__':
    app.run(debug=True)