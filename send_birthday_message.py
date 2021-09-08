import requests
import random
import datetime
import time

import vk_api
import schedule

from datetime import datetime
from settings import vk_token
from bs4 import BeautifulSoup

session = vk_api.VkApi(token=vk_token)
vk = session.get_api()

URL = 'https://klike.net/982-krasivye-kartinki-s-dnem-rozhdeniya-50-otkrytok.html'
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


def get_html():
    return requests.get(URL, headers=HEADERS)


def parse_web_site():
    html = get_html()
    try:
        href_content = get_content(html.text)
        return add_content(href_content)
    except ConnectionError:
        session.method("messages.send", {"user_id": 171189603,
                                         "random_id": get_rand_id(),
                                         "message": 'В работе программы произошла ошибка!'
                                         }),
        exit()


def get_content(html):
    main_url = "https://klike.net"
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img', class_='fr-dib')
    return [main_url + x.get("src") for x in images]


def add_content(href_content):
    image_url = requests.get(random.choice(href_content))
    with open('image.jpg', 'wb') as f:
        f.write(image_url.content)
    vk_method = vk.photos.getMessagesUploadServer()
    req = requests.post(vk_method['upload_url'], files={'photo': open('image.jpg', 'rb')}).json()
    photo_in_server = vk.photos.saveMessagesPhoto(photo=req['photo'], server=req['server'], hash=req['hash'])[0]
    image = f"photo{photo_in_server['owner_id']}_{photo_in_server['id']}"
    return image


def get_friends_birthday_info():
    friends = session.method('friends.search', {'user_id': 171189603, 'count': 1000, 'fields': 'bdate'})
    return friends['items']


def send_birthday_message():
    for friend in filter(lambda friend: 'bdate' in friend, get_friends_birthday_info()):
        compare_birthday_with_today(
            '.'.join(friend['bdate'].split('.')[:2]),
            friend['id']
        )


def compare_birthday_with_today(day_and_month, vk_friend_id):
    date_birthday = datetime.strptime(day_and_month, '%d.%m')
    if date_birthday.month == datetime.now().month and date_birthday.day == datetime.now().day:
        send_message(vk_friend_id, parse_web_site())
        print('сегодня День Рождения у ', vk_friend_id)
    else:
        print('сегодня нет праздника у :', vk_friend_id)


def time_to_send_message(time_to_run):
    schedule.every().day.at(time_to_run).do(send_birthday_message)
    while True:
        schedule.run_pending()
        time.sleep(1)


def send_message(friend_id, image): session.method("messages.send", {"user_id": friend_id,
                                                                     "random_id": get_rand_id(),
                                                                     "attachment": image
                                                                     }),


def get_rand_id():
    """2147483647 - max int32. 10 значное число необходимо для id"""
    random_id = random.randrange(1000000000, 2147483647, 1)
    return random_id


if __name__ == "__main__":
    time_to_send_message('15:35')
    # send_birthday_message()
