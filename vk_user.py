import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple

class VkUser:

    def __init__(self, group_token, user_token, upload):
        self.offset = 0
        self.url = 'https://api.vk.com/method/'
        self.group_params = {'access_token': group_token, 'v': '5.131'}
        self.user_params = {'access_token': user_token, 'v': '5.131'}
        self.rel_dict = {}
        self.last_show = {}
        self.upload = upload


    def gets_client(self, client_id):

        client_url = self.url + 'users.get'
        client_params = {'user_ids': client_id, 'fields': 'sex, city, bdate, screen_name'}

        params = {**self.user_params, **client_params}
        response = requests.get(client_url, params=params)
        items = response.json()['response'][0]
        items_keys = list(items.keys())

        vk_user_id = items['id']
        screen_name = items['screen_name']
        vk_link = 'https://vk.com/' + f'{screen_name}'
        first_name = items['first_name']
        last_name = items['last_name']

        gender = items['sex'] if 'sex' in items_keys else 1
        city = items['city']['id'] if 'city' in items_keys else 1
        bdate = items['bdate'] if 'bdate' in items_keys else '01.01.2020'

        if bdate.count('.') == 2:
            age = int((datetime.now() - datetime.strptime(bdate, "%d.%m.%Y")).days / 365)
        else:
            age = 23

        lst = ['user_id', 'vk_link', 'first_name', 'last_name', 'gender', 'city', 'age']
        Client = namedtuple('Client', lst)
        client = Client(vk_user_id, vk_link, first_name, last_name, gender, city, age)

        return client


    def rel_search(self, gender=0, city=0, age=40):

        rel_list = []
        age = age if age >= 23 else 23

        client_url = self.url + 'users.search'
        gender = {1: 2, 2: 1, 0: 0}[gender]
        search_params = {'status': 6,
                         'city': city,
                         'sex': gender,
                         'age_from': age-5,
                         'age_to': age+5,
                         'has_photo': 1,
                         'count': 1000}

        params = {**self.user_params, **search_params}
        response = requests.get(client_url, params=params)
        items = response.json()['response']['items']

        for item in items:
            if not item['is_closed']:
                rel_list.append(item['id'])

        return rel_list

    def rel_info(self, user_id):
        client = self.gets_client(user_id)
        first_name = client.first_name
        last_name = client.last_name
        vk_link = client.vk_link

        return first_name, last_name, vk_link


    def get_photos(self, user_id):
        photos_url = self.url + 'photos.get'
        photos_params = {'owner_id': user_id,
                         'offset': 0,
                         'album_id': 'profile',
                         'extended': 1,
                         'photo_sizes': 0,
                         'rev': 1}
        params = {**self.user_params, **photos_params}
        response = requests.get(photos_url, params=params)
        items = response.json()['response']['items']
        links_row = []

        for item in items:
            photo_item = ()
            photo_url, max_size = '', 0
            for sizes in item['sizes']:
                if sizes['height'] * sizes['width'] >= max_size:
                    max_size = sizes['height'] * sizes['width']
                    photo_url = sizes['url']
            photo_item += (photo_url,)
            likes = item['likes']['count']
            photo_item += (likes,)
            links_row.append(photo_item)

        links_row = sorted(links_row, key=lambda x: x[1], reverse=True)

        photo_links = [link[0] for link in links_row[0:3]]

        with ThreadPoolExecutor(max_workers=len(photo_links)) as pool:
            downloaded = tuple(pool.map(self.download, photo_links))

        return list(downloaded)

    def download(self, link):
        image = requests.get(link, stream=True)
        photo = self.upload.photo_messages(photos=image.raw)[0]
        owner_id, id = photo['owner_id'], photo['id']
        return f'photo{owner_id}_{id}'