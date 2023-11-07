from flask import Flask, request, redirect, url_for
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash # Para criptografar a senha
from flask import jsonify, Flask, request
import requests
from datetime import datetime
from bson.objectid import ObjectId


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@projagil.d9zuddb.mongodb.net/db_projeto"
mongo = PyMongo(app)

collection_usuarios = mongo.db.Usuarios
collection_mensagens = mongo.db.Mensagens
collection_remedios = mongo.db.Remedios

url_base = 'http://127.0.0.1:5000'

# 1- Login

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
            return "Login concluído", 200
        else:
            return jsonify("Nome de usuário e/ou senha inválido(s)"), 400


# 2- Cadastro

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_usuario():
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
        
        if "@" not in email:
            return jsonify("E-mail inválido."), 400
     
        else:
            collection_usuarios.insert_one({'username': usuario, 'email': email, 'password': senha})
            return "Usuário cadastrado", 200

# envia informações do usuário para o servidor
def send_user_to_server(username, email, password):
    response = requests.post(f'{url_base}/cadastro', data={'username': username, 'email': email, 'password': password})
    if response.status_code == 200:
        return True
    else:
        return False
        
# 3- Comunidade

@app.route('/send_message', methods=['POST'])
def send_message(): 
    if request.method == 'POST':
        message = request.form['message']
        if message:
            current_time = datetime.now().strftime('%H:%M %Y-%m-%d')
            collection_mensagens.insert_one({'message': message, 'datetime': current_time})
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
        for message in messages:
            message["_id"] = str(message["_id"])
        return jsonify(messages)
    
def get_messages_from_server():
    response = requests.get(f'{url_base}/get_messages')
    if response.status_code == 200:
        print(response.status_code)
        return response.json() 
    else:
        return []
    

# 4- Remédios
    
@app.route('/remedios', methods=['POST'])
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


def send_remedio_to_server(remedio):
    response = requests.post(f'{url_base}/remedios', data={'remedio': remedio})
    if response.status_code == 200:
        return True
    else:
        return False

@app.route('/remedios/<id_usuario>', methods=['GET'])
def get_remedios(id_usuario):
    if request.method == 'GET':
        remedios = list(collection_remedios.find({"_id": ObjectId(id_usuario)}))
        for remedio in remedios:
            remedio["_id"] = str(remedio["_id"])
        return remedios
    
def get_remedios_from_server():
    response = requests.get(f'{url_base}/remedios')
    if response.status_code == 200:
        print(response.status_code)
        return response.json() 
    else:
        return []

if __name__ == '__main__':
    app.run(debug=True)