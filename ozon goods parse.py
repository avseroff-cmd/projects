from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs4
from bs4.element import Tag
import requests
import re
import json
from telegram import Bot, InputMediaPhoto
from telegram.constants import ParseMode
import asyncio
import io
import time
import os
from datetime import date

driver = webdriver.Firefox()

def pageOpen(url):
    driver.get(url)
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ozonTagManagerApp")))
    finally:
        return driver.page_source

def scrape_category(category):
    url = f"https://www.ozon.ru/category/{category}/"
    captured_data = []
    item_counter = 0
    for page in range(1, 18):
        source_text = pageOpen(f'{url}?&page={page}')
        result = re.sub(r'<!.*?->', '', source_text)
        soup = bs4(result, 'html.parser')
        items_body = soup.find('div', id='paginatorContent')
        items = items_body.div.div
        for sibling in items:
            if isinstance(sibling, Tag) and sibling.text:
                span_name = sibling.find('span', class_='tsBody500Medium')
                if span_name is not None:
                    name = span_name.text
                else:
                   name = 0
                span_price = sibling.find('span', class_='c3015-a1 tsHeadline500Medium c3015-c0')
                if span_price is not None:
                    price = span_price.text
                else:
                   price = 0
                img_title = sibling.find('img', class_='jo0_23 b916-a')
                if img_title is not None:
                    img = img_title['srcset']
                    img = img.rsplit(' ', 2)[0]
                else:
                   img = 0  
                link_https = sibling.find('a', class_='oj2_23 tile-hover-target')
                if link_https is not None:
                    link_dirt = link_https['href']
                    parts = link_dirt.split('&keywords=')
                    new_link = parts[0]
                    link = ('https://www.ozon.ru' + new_link)
                else:
                    link = 0
                span_feedback = sibling.find('span', style='color:rgba(0, 26, 52, 0.6);')
                if span_feedback is not None:
                    feedback = span_feedback.text
                else:
                    feedback = 0
                if img!= 0 and feedback!= 0:
                    captured_data.append({
                        'name': name,
                        'price': price,
                        'img': img,
                        'link': link,
                        'feedback': feedback
                    })
                    item_counter += 1
                    if item_counter >= 20:
                        break
        if item_counter >= 20:
            break
    directory = 'C:/Users/avser/Desktop/OZON/ozon shmot/jsons'
    filename = f"{category}_{date.today().strftime('%Y-%m-%d')}.json"
    with open(os.path.join(directory, filename), 'w', encoding='utf-8') as f:
        json.dump(captured_data, f, ensure_ascii=False, indent=4)

categories = ['platya-zhenskie-7502', 'dzhinsy-zhenskie-7503', 'bluzy-i-rubashki-zhenskie-7511', 'sumki-zhenskie-17001', 'yubki-zhenskie-7504', 'tolstovki-i-olimpiyki-zhenskie-7788']

for cat in categories:
    scrape_category(cat)

directory = 'C:/Users/avser/Desktop/OZON/ozon shmot/jsons'

filename = 'final.json'

combined_data = []

json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

data_from_files = []

for file in json_files:
    with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
        data = json.load(f)
    data_from_files.append(data)

shuffled_data = []

while any(data_from_files):
    for i, data in enumerate(data_from_files):
        if data:
            shuffled_data.extend(data[:2])
            del data[:2]

with open(os.path.join(directory, filename), 'w', encoding='utf-8') as f:
    json.dump(shuffled_data, f, ensure_ascii=False, indent=4)

print(len(shuffled_data))

driver.quit()

bot_token = ''
channel_id = ''
objects_per_post = 2

async def post_images(data):
    bot = Bot(bot_token)
    for i in range(0, len(data), objects_per_post):
        media = []
        captions = []
        for item in data[i:i+objects_per_post]:
            response = requests.get(item["img"])
            bio = io.BytesIO(response.content)
            bio.name = 'image.jpg'
            media.append(InputMediaPhoto(media=bio))
            captions.append("🎀 [{}]({}) - {} ⭐️{}".format(item["name"], item["link"], item["price"], item["feedback"]))
        caption_text = '\n\n'.join(captions) + "\n\nКакой товар больше понравился?\n❤️- первый\n🔥- второй"
        await bot.send_media_group(chat_id=channel_id, media=media, caption=caption_text, parse_mode=ParseMode.MARKDOWN)
        time.sleep(32)

directory = "C:/Users/avser/Desktop/OZON/ozon shmot/jsons/final.json"
async def main():
    with open(directory, encoding='utf-8') as f:
        data = json.load(f)
    await post_images(data)

if __name__ == '__main__':
    asyncio.run(main())