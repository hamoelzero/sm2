from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
import os
from keep_alive import keep_alive


page_number=2
url=f'https://api.openloot.com/v2/market/listings?gameId=56a149cf-f146-487a-8a1c-58dc9ff3a15c&onSale=true&page={page_number}&sort=name%3Aasc'
current_prices={}

#setup options
try:
    keep_alive()
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
except:
    os.system("python3 restarter")

#executin js code
try:
    ################set current prices########################
    content=driver.execute_script("return fetch(arguments[0]).then(r => r.ok ? r.json() : console.log('test'))",url)
    responses=content["items"]
    for item in responses:
        current_prices[item["metadata"]["name"]] = item["minPrice"]
    print(current_prices)
    #############scraping loop##################################
    while True:
        time.sleep(4)
        content=driver.execute_script("return fetch(arguments[0]).then(r => r.ok ? r.json() : console.log('test'))",url)
        items=content["items"]
        for item in items:
            item_min_price = item["minPrice"]
            item_name = item["metadata"]["name"]
            current_item_price = current_prices[item_name]
            archetypeId = item["metadata"]["archetypeId"]
            differ = current_item_price - item_min_price
            differ_percent = (differ / current_item_price) * 100
            if item_name not in current_prices.keys():
                current_prices[item_name] = item_min_price
            if differ_percent > 10  :
                fetch_deal=driver.execute_script("return fetch(arguments[0]).then(r => r.ok ? r.json() : console.log('test'))",f"https://api.openloot.com/v2/market/listings/{archetypeId}/items?onSale=true&page=1&pageSize=48&sort=price%3Aasc")
                first_deal = fetch_deal["items"][0]
                deal_id = first_deal["orderId"]
                total_items = fetch_deal["totalItems"]
                fetch_deal = fetch_deal["items"][0]
                deal_id = fetch_deal["orderId"]
                buy_link = f"https://openloot.com/checkout?orderIds=%7D{deal_id}%7D"
                issued_number = fetch_deal["item"]["issuedId"]
                new_price = fetch_deal["price"]
                rarity = fetch_deal["item"]["metadata"]["rarity"]
                img = fetch_deal["item"]["metadata"]["imageUrl"]
                color = ""
                rarity_id = ""
                        
                if rarity == "common":
                    color = "ffffff"
                    rarity_id = "1089000885486616666"
                elif rarity == "uncommon":
                    color = "1cbf6b"
                    rarity_id = "1088999273271668797"
                elif rarity == "rare":
                    color = "159cfd"
                    rarity_id = "1088999061232824483"
                elif rarity == "epic":
                    color = "a369ff"
                    rarity_id = "1088998880705789952"
                elif rarity == "legendary":
                    color = "ef8320"
                    rarity_id = "1088999423914299464"
                elif rarity == "mythic":
                    color = "ffd42a"
                    rarity_id = "1088999547440734238"
                elif rarity == "exalted":
                    color = "fe5b7f"
                    rarity_id = "1088999659541897267"
                elif rarity == "exotic":
                    color = "d200ff"
                    rarity_id = "1190291989376270367"
                elif rarity == "transcendent":
                    color = "f30000"
                    rarity_id = "1190290233783226408"
                else:####unique rarity
                    color = "f368e0"
                    rarity_id = "1190296506343895080"
                deal_info = {
                                "issued_number":issued_number,
                                "item_name":item_name,
                                "differ":differ,
                                "differ_percent":differ_percent,
                                "old_price": current_item_price,
                                "new_price":new_price,
                                "rarity_id":rarity_id,
                                "img":img,
                                "buy_link":buy_link,
                                "check_button_url": f"https://openloot.com/items/{archetypeId.replace('_', '/', 1)}",
                                "total_items":total_items,
                                "color":color,
                                }
                print(deal_info)
                requests.post("https://main-server-mpmt.onrender.com/post_deal",json=deal_info,headers={
                    "Content-Type":"application/json"
                })
                current_prices[item_name] = item_min_price
            else:
                current_prices[item_name] = item_min_price


except:
    pass