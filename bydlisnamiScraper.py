import requests
from bs4 import BeautifulSoup
from model.flat import Flat
from traceback import print_exc
import re


class Scraper:
    def __init__(self):
        baseUrl = "https://www.bydlisnami.cz/nemovitosti?Ads%5Badvert_function%5D=1&Ads%5Badvert_type%5D=1&Ads%5BfromPrice%5D=0&Ads%5BtoPrice%5D=6+000+000&Ads%5Badvert_subtype%5D%5B%5D=5&Ads%5Badvert_subtype%5D%5B%5D=6&Ads%5Badvert_subtype%5D%5B%5D=7&Ads%5Badvert_subtype%5D%5B%5D=8&Ads%5Badvert_subtype%5D%5B%5D=9&Ads%5Bownership%5D%5B%5D=1&Ads%5BfromEstateArea%5D=&Ads%5BtoEstateArea%5D=&Ads%5BfromUsableArea%5D=&Ads%5BtoUsableArea%5D=&Ads%5Bloc_region_id%5D=1&Ads%5Bloc_city_id%5D=&Ads%5Bq%5D=&Ads_sort=top_date.desc&mobile_advert_type=1&mobile_loc_region=1"
        #baseUrl = "https://www.bezrealitky.cz/vypis/nabidka-prodej/byt/praha/2-1,3-kk,3-1,4-kk,4-1?priceTo=6%20000%20000&ownership%5B0%5D=osobni&construction%5B0%5D=cihla&surfaceFrom=50&_token=uOlMs5mRlC581leMdI66w1fRQs6Q_qOSPe2YbqBuiK8"
        urls = [baseUrl + "=&yt0="]
        self.flats = []
        for i in range(1,39):
            url = baseUrl + "&p=" + str(i) + "&yt0="
            urls.append(url)



        self.parse_pages(urls)

    def parse_pages(self,urls):
        for url in urls:
            print(url)
            response = requests.get(url,verify=False)
            soup = BeautifulSoup(response.content,'html.parser',fromEncoding='utf-8')



            mydivs = soup.findAll("div", {"class": "listview-item"})


            self.parse_posts(mydivs)

    def parse_post(self,div):
        # print(div)
        location = div.find('h3').find('a').text
        price = div.find("span", class_="price").text.replace("Kč", "").strip()
        # price2 = price.replace("\\xa0790","")
        price = price.encode("ascii", errors="ignore").decode()
        try:
            price = int(price)
        except ValueError as e:
            raise Exception(e)
        # print(div)
        suburb = ""
        # suburb = location.split('-')[1].split(',')[0].strip()
        try:
            location_splitted = location.split(",")
            size = int(location_splitted[-1].replace("m2", "").strip())
            rooms = location_splitted[0].replace("Prodej bytu", "").strip()
            room_base_coeff = int(rooms.split('+')[0])
            room_addons_coeff = 0.0 if "kk" in rooms else 0.5
            room_coeff = room_base_coeff + room_addons_coeff
            price_per_meter = price / size

            desc = div.find('p', class_="hidden-sm").text.strip()
        except ValueError as e:
            
            raise Exception(e)

        if "panel" in desc or "ateliér" in desc:
            #print("panel")
            raise Exception("not wanted - panel or atelier")

        #print(location, suburb, size, rooms, room_coeff, price, price_per_meter, desc)

        heading = div.find("h3", class_='list').text.strip()
        meters = heading.replace("Prodej bytu", "").replace("m2", "")

        splitted = meters.split(',')
        size = splitted[len(splitted)-1].strip()

        size = int(size)
        price = div.find("span", class_="price").text.strip().replace("Kč", "").replace(".", "").replace(" ","").strip()
        price = price.encode("ascii", errors="ignore").decode()
        price = int(price)

        price_per_meter = price / size

        price_per_room = price / room_coeff

        link = "https://www.bydlisnami.cz" + div.find("h3").find("a")['href']

        try:
            floor, penb, state = self.parse_details(link,desc)
        except Exception as e:
            return False
        if "investice do" in desc or "rezervováno" in desc.lower():
            return False

        flat = Flat(
            id=id,
            price=price,
            title=location,
            link=link,
            size=room_coeff,
            meters=size,
            price_per_meter=price_per_meter,
            floor=floor,
            penb=penb,
            state=state,
            description=desc
        )
        print(flat.get_cmp_dict())
        #print(location, suburb, price, room_coeff, rooms, size, price_per_meter, price_per_room)
        # print(div)



    def parse_posts(self,posts):

        for div in posts:
            try:
                self.parse_post(div)
            except Exception as e:
                if "cena" not in str(e) and "panel" not in str(e) and "Dražba" not in str(e):
                    print(e)
                    print_exc()
                    print(div)

                    exit(0)
                continue




    def parse_details(self, link, desc):
        floor = "N/A"
        state = "N/A"
        penb = "N/A"

        response = requests.get(link, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser', fromEncoding='utf-8')

        table = soup.find("table", {"class": "detail-view"})

        desc = soup.find("p", {"class": "text-justify"}).text


        #print(link)
        #print(desc, end='')
        #print(table)
        regex = r'([0-9])(?=. patře)'

        result = re.search(regex, desc).span()


        dt = table.find_all("th")
        dd = table.find_all("td")

        for dt, dd in zip(dt, dd):
            if "Třída energetické náročnosti" in dt.text:
                penb = dd.text

            if "Stavba" in dt.text and "Panelová" in dd.text:
                raise Exception("panel")

            if "Stav objektu" in dt.text:
                state = dd.text.strip()
        if result != None:

            floor = desc[result[0]:result[1]]
            floor = int(floor)

        if floor == "N/A":
            raise Exception("not known floor")

        return floor, penb, state

Scraper()