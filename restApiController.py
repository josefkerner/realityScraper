from lib.DBConnector import DBConnector
from model.flat import Flat
from sqlalchemy import and_, or_, not_

class RestApiController:
    def __init__(self):
        self.init_db()
    def init_db(self):
        connectionString = "postgresql://postgres:root@127.0.0.1/reality"
        self.db = DBConnector(connectionString)

    def set_interest_level(self,id, interest_level):
        flat = self.db.session.query(Flat).filter(Flat.id == id).one()
        flat.interest_level = interest_level
        self.db.session.commit()

    def get_flats(self):
        flats = self.db.session.query(Flat).filter(and_(
            Flat.interest_level != 0,
            Flat.price < 5600000,
            Flat.state != 'před rekonstrukcí'
        )).all()

        flats = [flat.get_cmp_dict() for flat in flats]

        return flats