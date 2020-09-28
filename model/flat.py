from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,Float, TIMESTAMP, Text
Base = declarative_base()
from datetime import date

class Flat(Base):
    __tablename__ = "flat"
    id = Column(String,primary_key=True)
    price = Column(Integer)
    title = Column(String)
    link = Column(String)
    size = Column(Float)
    meters = Column(Integer)
    price_per_meter = Column(Integer)
    floor = Column(Integer)
    penb = Column(String)
    state = Column(String)
    interest_level = Column(Integer)
    downloaded_at = Column(TIMESTAMP)
    description = Column(Text)

    def __init__(self,
                 id,
                 price,
                 title,
                 link,
                 size,
                 meters,
                 price_per_meter,
                 floor,
                 penb,
                 state,
                 description,
                 interest_level=5):
        self.id = id
        self.price = price
        self.title = title
        self.link = link
        self.size = size
        self.meters = meters
        self.price_per_meter = price_per_meter
        self.floor = floor
        self.penb = penb
        self.state = state
        self.interest_level = interest_level
        self.downloaded_at = date.today()
        self.description = description

    def adjust_interest_level(self):
        updated = False
        if self.description == None:
            return updated
        if "aukce" in self.description or "dražba" in self.description:
            self.interest_level = 4
            updated = True
        if "k rekonstrukci" in self.description:
            self.interest_level = 4
            updated = True
        if "rezervo" in self.description.lower():
            self.interest_level = 4
            updated = True
        return updated

    def get_cmp_dict(self):
        cmp_dict = {
            "id": self.id,
            "title" : self.title,
            "price" : self.price,
            "size" : self.size,
            "meters" : self.meters,
            "price_per_meter" : self.price_per_meter,
            "description": self.description,
            "floor" : self.floor,
            "penb" : self.penb,
            "state" : self.state,
            "link": self.link,
            "interest_level": self.interest_level

        }
        return cmp_dict

    '''
        :param ex = existing flat from internal database
    '''
    def update(self, ex):
        updated = False
        if self.price != ex.price and self.price != None:
            self.price = ex.price
            self.price_per_meter = ex.price / self.meters
            updated = True
        if self.description != ex.description and self.description != None:
            self.description = ex.description
            updated = True
        return updated