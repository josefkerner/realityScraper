from bezRealitky import Scraper as bezrealitky
from realityIdnes import Scraper as realityIdnes
from centrumReality import Scraper as centrumReality
from sreality import Scraper as sReality
import pandas as pd
from Levenshtein import distance as levenshtein_distance
from lib.DBConnector import DBConnector
from model.flat import Flat
from traceback import print_exc
import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, not_
import asyncio

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

        print('INFO - new flat',flat.link)
        return False

    async def load_flats(self):

        tasks = []

        for scraper in self.scrapers:
            task = self.loop.create_task(self.run_scraper(scraper))
            tasks.append(task)
        await asyncio.wait(tasks)


    async def run_scraper(self,scraper):
        print('triggering scraper',scraper)
        flats = scraper.start_workflow()
        for flat in flats:
            self.all_flats.append(flat)
        await asyncio.sleep(0.0001)




    def start_workflow(self):
        self.loop = asyncio.get_event_loop()
        print('INFO - starting flats load')
        self.loop.run_until_complete(self.load_flats())
        self.loop.close()

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
                            
                self.delete_not_existing_flats(self.all_flats)
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
    scraper.start_workflow()
    scraper.show_db_results()