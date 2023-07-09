import time
import requests
from datetime import datetime


class VkUser:

    def __init__(self, group_token, user_token):
        self.offset = 0
        self.url = 'https://api.vk.com/method/'
        self.group_params = {'access_token': group_token, 'v': '5.131'}
        self.user_params = {'access_token': user_token, 'v': '5.131'}


    def gets_client(self, client_id):

        client_url = self.url + 'users.get'
        client_params = {'user_ids': client_id,
                         'fields': 'sex, city, bdate, screen_name'}

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
            age = int((datetime.now() -
                       datetime.strptime(bdate, "%d.%m.%Y")).days / 365)
        else:
            age = 23

        return vk_user_id, vk_link, first_name, last_name, gender, city, age


    def get_relationship(self, gender=0, city=0, age=40):

        client_url = self.url + 'users.search'
        gender = {1: 2, 2: 1, 0: 0}[gender]
        search_params = {'relation': 6,
                         'city': city,
                         'sex': gender,
                         'age_from': age-5,
                         'age_to': age+5,
                         'count': 1,
                         'has_photo': 1}

        params = {**self.user_params, **search_params, 'offset': self.offset}
        response = requests.get(client_url, params=params)
        items = response.json()
        client_id = items['response']['items'][0]['id']
        closed_page = items['response']['items'][0]['is_closed']
        self.offset += 1

        while closed_page:
            params = {**self.user_params, **search_params, 'offset': self.offset}
            response = requests.get(client_url, params=params)
            items = response.json()
            client_id = items['response']['items'][0]['id']
            closed_page = items['response']['items'][0]['is_closed']
            time.sleep(0.34)
            self.offset += 1

        return client_id


    def get_photos(self, user_id):
        photos_url = self.url + 'photos.get'
        photos_params = {'owner_id': user_id,
                         'offset': 0,
                         'album_id': 'profile',
                         'extended': 1,
                         'photo_sizes': 0,
                         'rev': 1,
                         'count': 100}
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
        return photo_links