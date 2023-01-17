from flask import Flask, jsonify
from flask_restful import Api
from sql_alchemy import banco 
from flask_jwt_extended import JWTManager

from resources.hotel import Hoteis, Hotel
from resources.usuario import Usuario, UserRegister, UserLogin, UserLogout
from blacklist import BLACKLIST

app = Flask(__name__)

# Criar conexão com o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'DontTellAnyone'
app.config['JWT_BLACKLIST_ENABLED'] = True

api = Api(app)

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def verifica_blascklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST

@jwt.revoked_token_loader
def token_de_acesso_invalido(jwt_header, jwt_payload):
    return jsonify({'mensagem': 'Você não esta logado'}), 401

@app.before_first_request
def cria_banco():
    banco.create_all()

api.add_resource(Hoteis, '/hoteis')
api.add_resource(Hotel, '/hoteis/<string:hotel_id>')
api.add_resource(Usuario, '/usuario/<int:id>')
api.add_resource(UserRegister, '/cadastro')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    banco.init_app(app)
    app.run(debug=True)
