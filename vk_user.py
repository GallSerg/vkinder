import requests
import vk_api
from datetime import datetime
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


class VkUser:
    """
    Class for using methods to listen message from the group,
     find users on base parameters (parameters of the user who writes to the group)
      and send photos of relationships.
    """
    url = 'https://api.vk.com/method/'

    def __init__(self, group_token, user_token, version):
        self.group_token = group_token
        self.user_token = user_token
        self.watched_ids = []
        self.favourites = []
        self.offset = 0
        self.group_params = {
            'access_token': group_token,
            'v': version
        }
        self.user_params = {
            'access_token': user_token,
            'v': version
        }

    def get_photos(self, user_id, album_id):
        """
        Gets 100 photos of user
        :param user_id:
        :param album_id:
        :return:
        """
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id,
            'offset': 0,
            'album_id': album_id,
            'extended': 1,
            'photo_sizes': 0,
            'rev': 1,
            'count': 100
        }
        response = requests.get(photos_url, params={**self.user_params, **photos_params})
        return response.json()

    @staticmethod
    def get_likes(photos_in_list):
        """
        Additional static function to get element with max likes count and its index
        :param photos_in_list:
        :return:
        """
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

    def get_three_max_like_photos(self, user_id):
        """
        Gets three photos (if there are no three photos in profile - gets one or two) from profile.
        :return:
        """
        three_photos_from_vk_max_likes = []
        cur_photo_json = self.get_photos(user_id, 'profile')
        for elem in cur_photo_json['response']['items']:
            photo = elem['sizes'][-1]
            photo['likes'] = elem['likes']['count']
            min_v, min_i = self.get_likes(three_photos_from_vk_max_likes)
            if len(three_photos_from_vk_max_likes) < 3:
                three_photos_from_vk_max_likes.append(photo)
            elif photo['likes'] < min_v:
                three_photos_from_vk_max_likes[min_i] = photo
        return three_photos_from_vk_max_likes

    def get_client(self, user_id):
        """
        Gets user data from VK profile and returns to the program
        :param user_id:
        :return: first_name, last_name, sex, city_id and age
        """
        client_url = self.url + 'users.get'
        client_params = {
            'user_ids': user_id,
            'fields': 'sex, city, bdate'
        }
        response = requests.get(client_url, params={**self.user_params, **client_params})
        resp = response.json()
        age = int((datetime.now() - datetime.strptime(resp['response'][0]['bdate'], "%d.%m.%Y")).days / 365)
        return resp['response'][0]['first_name'], resp['response'][0]['last_name'], \
            resp['response'][0]['sex'], resp['response'][0]['city']['id'], age

    def get_relationship(self, gender=0, city=0, age=40):
        """
        Gets 1 person with some search parameters based on initial user
        :param gender:
        :param city:
        :param age:
        :return:
        """
        fam_status = 1
        client_url = self.url + 'users.search'
        gender_dict = {1: 2, 2: 1, 0: 0}
        gender = gender_dict[gender]
        search_params = {
            'city': city,
            'sex': gender,
            'status': fam_status,
            'age_from': age-10,
            'age_to': age+10,
            'count': 1,
            'has_photo': 1
        }
        check_rel = True
        resp = {}
        while check_rel:
            response = requests.get(client_url, params={**self.user_params, **search_params, 'offset': self.offset})
            resp = response.json()
            elem = resp['response']['items'][0]
            if not elem['is_closed'] and elem['id'] not in self.watched_ids:
                check_rel = False
            self.offset += 1
        return resp['response']['items']

    def msg_listener(self):
        """
        Listening messages of the user and answering by persons with photos or favourites
        :return:
        """
        vk_session = vk_api.VkApi(token=self.group_token)
        vk = vk_session.get_api()

        upload = VkUpload(vk_session)
        longpoll = VkLongPoll(vk_session)

        person = {}
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.text.lower() in ['привет', 'hi', 'рш', 'ghbdtn', 'прив', 'начнем', 'старт']:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message="Привет, напиши 'далее' или 'поиск', чтобы найти вторую половинку"
                    )
                elif event.text.lower() in ['далее', 'continue', 'начнем поиск', 'поиск']:
                    print(f'id{event.user_id}: "{event.text}"', end=' ')
                    attachments = []
                    first_name, last_name, gender, city, age = self.get_client(event.user_id)
                    print(first_name, last_name, gender, city)
                    person = self.get_relationship(gender, city, age)[0]
                    user_id = person['id']
                    self.watched_ids.append(user_id)
                    photos = self.get_three_max_like_photos(user_id)
                    text = person['first_name'] + ' ' + person['last_name']
                    if photos:
                        for ph in photos:
                            image = requests.get(ph['url'], stream=True)
                            photo = upload.photo_messages(photos=image.raw)[0]
                            attachments.append(
                                f"photo{photo['owner_id']}_{photo['id']}"
                            )

                    vk.messages.send(
                        user_id=event.user_id,
                        attachment=','.join(attachments),
                        random_id=get_random_id(),
                        message=text
                    )
                    print('find user with id', user_id, 'response sent')

                elif event.text.lower() in ['добавить', 'add', 'lj,fdbnm', 'фвв']:
                    if person:
                        if person['id'] not in [key for i in self.favourites for key in i.keys()]:
                            self.favourites.append({person['id']: [person['first_name'], person['last_name']]})
                            vk.messages.send(
                                user_id=event.user_id,
                                random_id=get_random_id(),
                                message=f"{person['first_name']} {person['last_name']} добавлен(-а) в избранное"
                            )
                        else:
                            vk.messages.send(
                                user_id=event.user_id,
                                random_id=get_random_id(),
                                message=f"{person['first_name']} {person['last_name']} уже есть в избранном"
                            )
                    else:
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message='Сначала нужно сделать запрос'
                        )

                elif event.text.lower() in ['избранное', 'favourites', 'favourite', 'bp,hfyyjt']:
                    if self.favourites:
                        for elem in self.favourites:
                            for names in elem.values():
                                vk.messages.send(
                                    user_id=event.user_id,
                                    random_id=get_random_id(),
                                    message=' '.join(names)
                                )
                    else:
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message='У вас никого нет в избранном'
                        )
