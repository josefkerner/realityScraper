import requests
from bs4 import BeautifulSoup
from traceback import print_exc

from requests_html import HTMLSession
import time
from model.flat import Flat
class Scraper:
    def __init__(self):
        self.flats = []

        baseUrl = "https://www.sreality.cz/hledani/prodej/byty/praha?velikost=2%2B1,3%2Bkk,3%2B1,4%2Bkk&stavba=cihlova&vlastnictvi=osobni&stav=velmi-dobry-stav,dobry-stav,novostavby,po-rekonstrukci&plocha-od=50&plocha-do=10000000000&cena-od=0&cena-do=6000000"

        self.urls = [baseUrl+"&bez-aukce=1"]
        for i in range(1, 3):
            additionalUrl = baseUrl + "&strana=" + str(i) + "&bez-aukce=1"
            self.urls.append(additionalUrl)

    def start_workflow(self):
        self.parse_pages(self.urls)
        return self.flats

    def parse_pages(self, urls):
        # srealitky posts are rendered during runtime with JS, so we need to use selenium with JS support
        from selenium import webdriver
        self.driver = HTMLSession()
        #chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--headless')
        #self.driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

        #self.driver = webdriver.PhantomJS("C:\\dev\\phantomjs-2.1.1-windows\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")

        #soupFromJokesCC = BeautifulSoup(driver.page_source)  # page_source fetches page after rendering is complete
        #driver.save_screenshot('screen.png')  # save a screenshot to disk

        #driver.quit()
        for url in urls:

            #time.sleep(1) # sleep in order to not get blocked
            print("INFO -- parsing page")
            res = self.driver.get(url,headers={'user-agent':'Mozilla/5.0'})
            res.html.render(wait=1, sleep=5)
            #response = requests.get(url, verify=False)

            print(print(res.html.__dict__))


            soup = BeautifulSoup(res.html._html,'html.parser')
            print(url)
            #print(soup)

            posts = soup.find_all("div",class_="info")

            self.parse_posts(posts)

    def parse_posts(self,posts):
        for post in posts:

            start = time.time()

            location = post.find("span",class_="locality").text.strip()
            price = post.find("span", class_="norm-price").text.strip()
            heading = post.find("span",class_="name").text.strip()
            heading = heading.replace("Prodej bytu ","")
            heading = heading.encode("ascii", errors="ignore").decode()
            rooms = heading.split(' ')[0]
            room_base_coeff = int(rooms.split('+')[0])
            room_addons_coeff = 0.0 if "kk" in rooms else 0.5
            room_coeff = room_base_coeff + room_addons_coeff

            link = post.find("a",class_="title")['href']

            link = "https://sreality.cz" + link
            if price == "Info o ceně u RK":
                continue
            price = price.replace("Kč","")
            price = price.encode("ascii", errors="ignore").decode()
            price = int(price.replace(" ",""))

            try:
                meters = heading.replace('m', '').strip()
                meters = meters[-2:]
                meters = int(meters)
                price_per_meter = price / meters
                #print(location, price, room_coeff, meters, price_per_meter, link)

                floor, penb, state, desc = self.parse_post(link)

                id = link.split('/')[-1]

                flat = Flat(
                            id=id,
                            title=location,
                            size=room_coeff,
                            price=price,
                            price_per_meter=price_per_meter,
                            meters=meters,
                            link=link,
                            floor=floor,
                            penb=penb,
                            state=state,
                            description=desc
                            )
                self.flats.append(flat)
            except IndexError as ie:
                print('error',ie)
                #print(heading,ie)
            except ValueError as ve:
                print('error',ve)
                #print(heading,ve)
            #print(post)

            end = time.time()

            duration = end - start

            print('post parsed in ',duration)

    def parse_post(self,link):
        floor = 1000
        penb = "N/A"
        state = "N/A"

        try:

            res = self.driver.get(link)
            res.html.render(wait=1, sleep=5, keep_page=True)
            soup = BeautifulSoup(res.html._html,"html.parser")

            params = soup.find("div",class_="params")

            desc = ""

            if params == None:
                #print(soup)
                print('params not found for',link)
                print(soup)
                raise ValueError("Could not find params")

            else:
                print("got params")
                #raise ValueError("Could not find params div")
            labels = params.find_all("li",class_="param")

            for param in labels:

                label = param.find("label",class_="param-label").text.strip()
                if "Energetická náročnost budovy" in label:
                    value = param.find("span").text.strip()
                    value = value.replace("Třída ",'')

                    penb = value.split('-')[0].strip()
                    penb = penb.replace("Třída ","")
                if "Stav objektu" in label:
                    value = param.find("span").text.strip()
                    state = value
                if "Podlaží" in label:
                    value = param.find("span").text.strip()
                    floor = value.split('.')[0]
            if floor == "přízemí":
                floor = 0
            floor = int(floor)

            return floor, penb, state, desc
        except Exception as e:
            print("------------------------")
            print(e.__class__.__name__,e)
            print_exc()
            print(link)
            raise ValueError(str(e))


if __name__ == "__main__":
    scraper = Scraper()
    scraper.start_workflow()

    flat_num = str(len(scraper.flats))
    print(flat_num + " flats were scraped from sreality")
    for flat in scraper.flats:
        print(flat.get_cmp_dict())

