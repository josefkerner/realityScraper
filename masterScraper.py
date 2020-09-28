from bezRealitky import Scraper as bezrealitky
from realityIdnes import Scraper as realityIdnes
from centrumReality import Scraper as centrumReality
from sreality import Scraper as sReality
import pandas as pd
from Levenshtein import distance as levenshtein_distance
from lib.DBConnector import DBConnector
from model.flat import Flat
from traceback import print_exc
import logging
import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, not_
import asyncio

class MasterScraper:
    def __init__(self):
        self.all_flats = []

        self.scrapers = [bezrealitky(),realityIdnes(),centrumReality()
            #,sReality() #TODO - shitty quality still - problem with parsing and IP stalling
                         ]

    def init_db(self):
        connectionString = "postgresql://postgres:root@127.0.0.1/reality"
        self.db = DBConnector(connectionString)
        
    def deduplicate_flats(self):

        print("Looking for duplicate flats")
        flats = self.db.session.query(Flat).all()
        flats_comp = self.db.session.query(Flat).all()
        duplicates = []
        for flat in flats:
            if flat.interest_level == 0:
                continue
            masterFlat = {'master_flat': flat,'duplicates': []}
            same_records = None
            for flat_comp in flats_comp:
                if flat_comp.interest_level == 0:
                    continue
                duplicate = False
                ids = [flat.id for flat in masterFlat['duplicates']]
                if flat.id == flat_comp.id:
                    continue # do not compare exactly same records
                if flat.price_per_meter == flat_comp.price_per_meter and flat.price == flat_comp.price:
                    if levenshtein_distance(flat.title, flat_comp.title) < 6:
                        if flat_comp.id not in ids:
                            duplicate = True
                if levenshtein_distance(flat.title, flat_comp.title) < 3:
                    if flat_comp.id not in ids:
                        if abs(flat.price - flat_comp.price) > 500000:
                            duplicate = False
                        else:
                            duplicate = True

                if duplicate:
                    masterFlat['duplicates'].append(flat_comp)
            if len(masterFlat['duplicates']) != 0:
                print("found same records")
                print('master',masterFlat['master_flat'].get_cmp_dict())
                for duplicate in masterFlat['duplicates']:
                    duplicate.interest_level = 3
                    self.db.session.commit()
                print('----------------------------------------------------')


    def check_existing(self, flat):
        try:
            ex_flat = self.db.session.query(Flat).filter(Flat.id == flat.id).one()
            ex_flat.update(flat)
            ex_flat.adjust_interest_level()
            self.db.session.commit()
            return True
        except NoResultFound as e:
            logging.info('INFO - new flat',flat.link)
            return False

    def load_flats(self):
        for scraper in self.scrapers:
            self.run_scraper(scraper)

    def run_scraper(self,scraper):
        print('triggering scraper',scraper)
        flats = scraper.start_workflow()
        for flat in flats:
            self.all_flats.append(flat)

    def start_workflow(self):
        self.load_flats()

        try:
                print('downloaded number of flats : ',len(self.all_flats))
                for flat in self.all_flats:
                    if self.check_existing(flat) == False:
                        try:
                            self.db.add_record(flat)

                            self.db.session.commit()
                            print('INFO : saved new flat')
                        except Exception as e:
                            print('failed to save flat of link', flat.link)
                            print('with exception', str(e))
                            continue

                self.deduplicate_flats()
                    
                            
                #self.delete_not_existing_flats(self.all_flats)
        except Exception as e:
            print("INFO - failed to process scraper",scraper," with error", str(e))
            print_exc()
            
    def delete_not_existing_flats(self,downloaded_flats):
        existing_flats = self.db.session.query(Flat).all()
        
        downloaded_ids = [flat.id for flat in downloaded_flats]
        
        for flat in existing_flats:
            if flat.id not in downloaded_ids:
                flat.interest_level = 0
                self.db.session.commit()

    def show_db_results(self):
        flats_all = []
        flats = self.db.session.query(Flat).filter(and_(
            Flat.interest_level > 4,
            Flat.price < 5600000,
            Flat.meters > 52,
            Flat.size > 2.0,
            Flat.price > 1000000,
            Flat.state != 'před rekonstrukcí'
        )).all()
        for flat in flats:
            flats_all.append(flat.get_cmp_dict())

        if len(flats_all) > 4:

            self.show_results(flats_all)
        else:
            print("No flats found with given conditions")
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
    scraper.start_workflow()
    #scraper.deduplicate_flats()
    scraper.show_db_results()