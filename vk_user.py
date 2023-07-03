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
            'count': 3
        }
        response = requests.get(photos_url, params={**self.user_params, **photos_params})
        self.cur_photo_json = response.json()
        return self.cur_photo_json

    @staticmethod
    def get_likes(self, photos_in_list):
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
            min_v, min_i = self.get_likes(self, three_photos_from_vk_max_likes)
            if len(three_photos_from_vk_max_likes) < 3:
                three_photos_from_vk_max_likes.append(photo)
            elif photo['likes']['count'] < min_v:
                three_photos_from_vk_max_likes[min_i] = photo
        return three_photos_from_vk_max_likes

    def msg_listener(self):
        vk_session = vk_api.VkApi(token=self.group_token)
        vk = vk_session.get_api()

        upload = VkUpload(vk_session)  # Для загрузки изображений
        longpoll = VkLongPoll(vk_session)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                print('id{}: "{}"'.format(event.user_id, event.text), end=' ')
                attachments = []
                user_id = 1
                self.get_photos(user_id, 'wall')
                photos = self.get_photos_params()
                text = 'Лайков: '
                if photos:
                    for ph in photos:
                        image = requests.get(ph['url'], stream=True)
                        text += str(ph['likes'])+', '
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
