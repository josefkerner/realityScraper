import json
import time
import requests, re
from bs4 import BeautifulSoup
from requests_html import HTMLSession

session = HTMLSession()
page=2
numberofresults=20
epochmiliseconds=round(time.time() * 1000)
paramsdict={
    "building_condition": "1|2|10|6",
"building_type_search": "2",
"category_main_cb": "1",
"category_sub_cb": "5|6|7",
"category_type_cb": "1",
"czk_price_summary_order2": "0|7000000",
"locality_region_id": "10",
"no_auction": "1",
"ownership": "1",
"per_page": "20",
"usable_area": "55|10000000000"

}
data=requests.get("https://www.sreality.cz/api/cs/v2/estates",params=paramsdict, verify=False).json()
for lead in data["_embedded"]["estates"]:
    locality=lead["seo"]["locality"]
    name=lead["name"]
    floor = None
    state = 5
    hash_id=lead["hash_id"]
    price = lead['price']
    typedata = str(name).split('Prodej bytu ')[1]
    typedata = typedata.split(' ')[0]
    typedata = typedata.split('\xa0')[0]

    #typedata=[s for s in name.split(" ") if "+" in s][0].replace("\u00a0"," ").split(" ")[0]
    link = f'https://www.sreality.cz/detail/prodej/byt/{typedata}/{locality}/{hash_id}'

    #print(lead)

    api_link = f"https://www.sreality.cz/api/cs/v2/estates/{hash_id}?tms=1638977495379"
    res = session.get(api_link,verify=False)

    rendered = res.html.render()
    resp = res.content.decode('utf-8')
    resp = json.loads(resp)
    locality = str(locality).split(' ')[0]
    meta = resp['meta_description']
    splitted = str(meta).split(' ')
    size = splitted[1]
    meters = int(splitted[2])
    price = str(str(meta).split(';')[1]).split(',')[0]
    price = str(price).replace('Kč','').replace(' ','')
    price = int(''.join(re.findall(r'\d+', price)))
    price_per_meter = price / meters

    text = resp['text']['value']
    floor_indicators = ['podzemním','ateliér','sníženém přízemí']
    for floor_indicator in floor_indicators:
        if floor_indicator in text:
            floor = 0
    if "původním stavu" in text:
        state = 2

    if floor == 0: continue
    if price_per_meter > 120000: continue
    if meters < 60: continue
    if state <3 : continue
    print(locality, size, meters, price, price_per_meter)
    print(link)
    #print(text)
