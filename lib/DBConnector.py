import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
class DBConnector:
    def __init__(self, connectionString):
        try:
            self.engine = db.create_engine(connectionString)
            self.connection = self.engine.connect()
            self.metadata = db.MetaData()
            self.metadata.bind = self.engine
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except ConnectionError as e:
            print(e)
    def add_record(self, record):
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record


    def update_or_add_record(self, record):

        self.add_record(record)
    def truncate_table(self,table_object):
        self.session.query(table_object).delete()