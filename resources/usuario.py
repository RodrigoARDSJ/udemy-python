import hmac
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from models.usuario import ModelUsuario
from blacklist import BLACKLIST
# from werkzeug.security import safe_str_cmp

atributos = reqparse.RequestParser()
atributos.add_argument(
    'login', type=str, help="O campo 'login' não pode ser deixado em branco!")
atributos.add_argument(
    'senha', type=str, help="O campo 'senha' não pode ser deixado em branco!")


# class Usuarios(Resource):
#    def get(self):
#        return {'hoteis': [hotel.json() for hotel in ModelHotel.find_all_hoteis()]}, 200


class Usuario(Resource):

    #    argumentos = reqparse.RequestParser()
    #    argumentos.add_argument('nome', type=str, required=True,
    #                            help="O campo 'nome' não pode ser vazio")
    #    argumentos.add_argument('estrelas', type=float, required=True,
    #                            help="O campo 'estrelas' não pode ser vazio")
    #    argumentos.add_argument('diaria', type=float, required=True,
    #                            help="O campo 'diaria' não pode ser vazio")
    #    argumentos.add_argument('cidade', type=str, required=True,
    # #                            help="O campo 'cidade' não pode ser vazio")

    #     def find_hotel(user_id):
    #         for usuario in usuarios:
    #             if usuario['id'] == user_id:
    #                 return None

    def get(self, id):
        usuario = ModelUsuario.find_user(id)
        if usuario:
            return usuario.json(), 200
        return {'message': 'Usuario não encontrado'}, 404

    # def post(self, hotel_id):
    #     if ModelHotel.find_hotel(hotel_id):
    #         return {"message": f"Hotel '{hotel_id}' já existe"}, 400

    #     dados = Hotel.argumentos.parse_args()
    #     hotel = ModelHotel(hotel_id, **dados)
    #     try:
    #         hotel.save_hotel()
    #     except:
    #         return {'mensagem': 'Ocorreu um erro interno ao tentar cadastrar um hotel'}, 500
    #     return hotel.json()

    # def put(self, hotel_id):

    #     dados = Hotel.argumentos.parse_args()

    #     hotel_encontrado = ModelHotel.find_hotel(hotel_id)

    #     if hotel_encontrado:
    #         hotel_encontrado.update_hotel(**dados)
    #         hotel_encontrado.save_hotel()
    #         return hotel_encontrado.json(), 200

    #     return {'message': 'hotel não encontrado'}, 404

    @jwt_required()
    def delete(self, id):
        del_usuario = ModelUsuario.find_user(id)
        if del_usuario:
            try:
                del_usuario.delete_user()
            except:
                return {'mensagem': 'Ocorreu um erro interno ao tentar cadastrar um usuario'}, 500
            return {}, 204
        return {'message': 'usuario não encontrado'}, 404


class UserRegister(Resource):

    def post(self):
        dados = atributos.parse_args()

        if ModelUsuario.find_by_login(dados['login']):
            return {"mensagem": f"O login {dados['login']} já existe"}, 400

        usuario = ModelUsuario(**dados)

        usuario.save_user()

        return {"mensagem": "Usuario criado com sucesso!"}, 201


class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        usuario = ModelUsuario.find_by_login(dados['login'])

        if usuario and hmac.compare_digest(usuario.senha, dados['senha']):
            token_de_access = create_access_token(identity=usuario.id)
            return {"access_token": token_de_access}, 201
        return {"mensagem": "Login ou senha está incorreto"}, 401

class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # JWT Token Identifier
        BLACKLIST.add(jwt_id)
        return {'mensagem': 'Logout efetuado com sucesso'}, 200