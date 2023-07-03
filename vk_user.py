import random
import requests
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, group_token, user_token, version):
        self.group_token = group_token
        self.user_token = user_token
        self.cur_photo_json = {}
        self.watched_ids = []
        self.group_params = {
            'access_token': group_token,
            'v': version
        }
        self.user_params = {
            'access_token': user_token,
            'v': version
        }

    def get_photos(self, user_id, album_id, offset=0):
        self.cur_photo_json = ''
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id,
            'offset': offset,
            'album_id': album_id,
            'extended': 1,
            'photo_sizes': 0,
            'rev': 1,
            'count': 300
        }
        response = requests.get(photos_url, params={**self.user_params, **photos_params})
        self.cur_photo_json = response.json()
        return self.cur_photo_json

    @staticmethod
    def get_likes(photos_in_list):
        if photos_in_list:
            min_i = 0
            min_v = photos_in_list[0]['likes']
        else:
            min_i = 0
            min_v = 0
        for index, elem in enumerate(photos_in_list):
            if elem['likes'] > min_v:
                min_v, min_i = elem['likes'], index
        return min_v, min_i

    def get_photos_params(self):
        three_photos_from_vk_max_likes = []
        for elem in self.cur_photo_json['response']['items']:
            photo = elem['sizes'][-1]
            photo['likes'] = elem['likes']['count']
            min_v, min_i = self.get_likes(three_photos_from_vk_max_likes)
            if len(three_photos_from_vk_max_likes) < 3:
                three_photos_from_vk_max_likes.append(photo)
            elif photo['likes'] < min_v:
                three_photos_from_vk_max_likes[min_i] = photo
        return three_photos_from_vk_max_likes

    def get_client(self, user_id):
        client_url = self.url + 'users.get'
        client_params = {
            'user_ids': user_id,
            'fields': 'sex, city'
        }
        response = requests.get(client_url, params={**self.user_params, **client_params})
        resp = response.json()
        return resp['response'][0]['first_name'], resp['response'][0]['last_name'], \
            resp['response'][0]['sex'], resp['response'][0]['city']['id']

    def get_relationship(self, gender=0, city=99999):
        fam_status = 1
        client_url = self.url + 'users.search'
        gender_dict = {1: 2, 2: 1, 0: 0}
        gender = gender_dict[gender]
        search_params = {
            'city': city,
            'sex': gender,
            'status': fam_status
        }
        response = requests.get(client_url, params={**self.user_params, **search_params})
        resp = response.json()
        return resp['response']['items']

    def msg_listener(self):
        vk_session = vk_api.VkApi(token=self.group_token)
        vk = vk_session.get_api()

        upload = VkUpload(vk_session)
        longpoll = VkLongPoll(vk_session)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.text.lower() in ['привет', 'hi', 'рш', 'ghbdtn', 'прив']:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Привет, напиши 'далее' или 'поиск', чтобы познакомиться"
                    )
                elif event.text.lower() in ['далее', 'continue', 'начнем поиск', 'поиск']:
                    print('id{}: "{}"'.format(event.user_id, event.text), end=' ')
                    attachments = []
                    first_name, last_name, gender, city = self.get_client(event.user_id)
                    print(first_name, last_name, gender, city)
                    relations = self.get_relationship(gender, city)
                    relations = [elem for elem in relations if not elem['is_closed']]
                    person = relations.pop(random.randrange(0, len(relations)))
                    user_id = person['id']
                    self.watched_ids.append(user_id)
                    self.get_photos(user_id, 'profile')
                    photos = self.get_photos_params()
                    text = person['first_name'] + ' ' + person['last_name']
                    if photos:
                        for ph in photos:
                            image = requests.get(ph['url'], stream=True)
                            photo = upload.photo_messages(photos=image.raw)[0]
                            attachments.append(
                                'photo{}_{}'.format(photo['owner_id'], photo['id'])
                            )

                    vk.messages.send(
                        user_id=event.user_id,
                        attachment=','.join(attachments),
                        random_id=get_random_id(),
                        message=text
                    )
                    print('find user with id', user_id, 'response sent')

                elif event.text.lower() in ['избранное', 'favourites', 'favourite', 'bp,hfyyjt']:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message='Увы, избранного пока нет'
                    )
