from bezRealitky import Scraper as bezrealitky
from realityIdnes import Scraper as realityIdnes
from centrumReality import Scraper as centrumReality
from sreality import Scraper as sReality
import pandas as pd
from Levenshtein import distance as levenshtein_distance
from lib.DBConnector import DBConnector
from model.flat import Flat

import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, not_

class MasterScraper:
    def __init__(self):
        self.all_flats = []

        self.scrapers = [bezrealitky(),realityIdnes(),centrumReality(),sReality()]

    def init_db(self):
        connectionString = "postgresql://postgres:root@127.0.0.1/reality"
        self.db = DBConnector(connectionString)

    def check_existing(self, flat):
        try:
            self.db.session.query(Flat).filter(Flat.id == flat.id).one()
            return True
        except NoResultFound as e:
            for ex_flat in self.all_flats:
                if flat.price_per_meter == ex_flat.price_per_meter:
                    return True
                if levenshtein_distance(flat.title,ex_flat.title) < 3:
                    return True
        return False

    def start_workflow(self):

        for scraper in self.scrapers:
            flats = scraper.start_workflow()

            for flat in flats:
                if not self.check_existing(flat):
                    self.db.add_record(flat)
                    self.all_flats.append(flat)
                    self.db.session.commit()

    def show_db_results(self,):
        flats_all = []
        flats = self.db.session.query(Flat).filter(and_(
            Flat.interest_level != 0,
            Flat.price < 5600000,
            Flat.state != 'před rekonstrukcí'
        )).all()
        for flat in flats:
            flats_all.append(flat.get_cmp_dict())

        self.show_results(flats_all)
    def show_results(self,flats):

        data = pd.DataFrame(flats)

        sorted = data.sort_values(by=['price_per_meter'])
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.width', 2000)
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('max_colwidth', 800)
        sorted.style.set_properties(**{'text-align': 'left'}).set_table_styles(
            [dict(selector='th', props=[('text-align', 'left')])])
        pd.option_context('display.colheader_justify', 'right')
        print(sorted)

if __name__ == "__main__":
    scraper = MasterScraper()
    scraper.init_db()
    #scraper.start_workflow()
    scraper.show_db_results()