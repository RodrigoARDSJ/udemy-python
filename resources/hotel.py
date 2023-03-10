from flask_restful import Resource, reqparse
from models.hotel import ModelHotel
from flask_jwt_extended import jwt_required
import sqlite3


def normalize_path_params(cidade=None,
                          estrelas_min=0,
                          estrelas_max=5,
                          diaria_min=0,
                          diaria_max=10000,
                          limit=20, offset=0,
                          **dados):
    if cidade:
        return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'cidade': cidade,
            'limit': limit,
            'offset': offset
        }
    return {
        'estrelas_min': estrelas_min,
        'estrelas_max': estrelas_max,
        'diaria_min': diaria_min,
        'diaria_max': diaria_max,
        'cidade': cidade,
        'limit': limit,
        'offset': offset
    }


path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrela_min', type=float)
path_params.add_argument('estrela_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)


class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave: dados[chave]
                         for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        # fazendo assim para pegar o parametro da requisição, tem menos chance de quebrar o codigo pq se o paramentro não existir, ele retorna None
        if not parametros.get('cidade'):
            consulta = "SELECT * FROM hoteis \
                        WHERE (estrelas > ? \
                        and estrelas < ?) \
                        and(diaria > ? ? and diaria < ?)\
                        LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)
        else:
            consulta = "SELECT * FROM hoteis \
                        WHERE (estrelas > ? \
                        and estrelas < ?) \
                        and(diaria > ? and diaria < ?)\
                        and cidade = ? LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)

        hoteis = []
        for linha in resultado:
            hoteis.append({
                'hotel_id': linha[0],
                'nome': linha[1],
                'estrelas': linha[2],
                'diaria': linha[3],
                'cidade': linha[4]
            })

        return {'hoteis': hoteis}, 200


class Hotel(Resource):

    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True,
                            help="O campo 'nome' não pode ser vazio")
    argumentos.add_argument('estrelas', type=float, required=True,
                            help="O campo 'estrelas' não pode ser vazio")
    argumentos.add_argument('diaria', type=float, required=True,
                            help="O campo 'diaria' não pode ser vazio")
    argumentos.add_argument('cidade', type=str, required=True,
                            help="O campo 'cidade' não pode ser vazio")

    def find_hotel(hotel_id):
        for hotel in hoteis:
            if hotel['hotel_id'] == hotel_id:
                return None

    def get(self, hotel_id):
        hotel = ModelHotel.find_hotel(hotel_id)
        if hotel:
            return hotel.json(), 200
        return {'message': 'Hotel não encontrado'}, 404

    @jwt_required()
    def post(self, hotel_id):
        if ModelHotel.find_hotel(hotel_id):
            return {"message": f"Hotel '{hotel_id}' já existe"}, 400

        dados = Hotel.argumentos.parse_args()
        hotel = ModelHotel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {'mensagem': 'Ocorreu um erro interno ao tentar cadastrar um hotel'}, 500
        return hotel.json()

    @jwt_required()
    def put(self, hotel_id):

        dados = Hotel.argumentos.parse_args()

        hotel_encontrado = ModelHotel.find_hotel(hotel_id)

        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200

        return {'message': 'hotel não encontrado'}, 404

    @jwt_required()
    def delete(self, hotel_id):
        del_hotel = ModelHotel.find_hotel(hotel_id)
        if del_hotel:
            try:
                del_hotel.delete_hotel()
            except:
                return {'mensagem': 'Ocorreu um erro interno ao tentar cadastrar um hotel'}, 500
            return {}, 204
        return {'message': 'Hotel não encontrado'}, 404
