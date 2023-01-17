from sql_alchemy import banco


class ModelUsuario(banco.Model):
    __tablename__ = "usuarios"

    id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40))
    senha = banco.Column(banco.String(40))

    def __init__(self, login, senha):
        self.login = login
        self.senha = senha

    def json(self):
        return {
            'id': self.id,
            'login': self.login,
        }
   
    @classmethod
    def find_all_users(cls):
        return cls.query.all()

    @classmethod
    def find_user(cls, id):
        user = cls.query.filter_by(id=id).first()
        if user:
            return user
        return None
    
    @classmethod
    def find_by_login(cls, login):
        user = cls.query.filter_by(login=login).first()
        if user:
            return user
        return None
    

    def save_user(self):
        banco.session.add(self)
        banco.session.commit()

#    def update_hotel(self, nome, estrelas, diaria, cidade):
#        self.nome = nome
#        self.estrelas = estrelas
#        self.diaria = diaria
#        self.cidade = cidade
    
    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()