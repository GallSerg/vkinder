import os
import time
import requests
import vk_api
from dotenv import load_dotenv
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from vkinder_db.model_db import create_tables
from vkinder_db.work_with_db import Database, connect_db
from vk_user import VkUser


def send_message(user_id, message, keyboard=None, attachments=None):
    """
    Basic parameters for sending a message.
    """
    param = {'user_id': user_id, 'message': message,
             'random_id': get_random_id()}

    if keyboard is not None:
        param['keyboard'] = keyboard.get_keyboard()
    if attachments is not None:
        param['attachment'] = ','.join(attachments)
        param['random_id'] = get_random_id()

    vk_session.method('messages.send', param)


if __name__ == '__main__':

    sessions, engine = connect_db()
    db_manage = Database(sessions)
    create_tables(engine)

    load_dotenv()
    group_token = os.environ['vk_group_token']
    user_token = os.environ['vk_bot_token']

    vk_session = vk_api.VkApi(token=group_token)
    vk = vk_session.get_api()

    upload = VkUpload(vk_session)
    longpoll = VkLongPoll(vk_session)

    vk_manage = VkUser(group_token, user_token)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text.lower()
            user_id = event.user_id

            vk_user_id, vk_link, first_name, last_name, \
                gender, city, age = vk_manage.gets_client(user_id)

            if not db_manage.check_user(vk_user_id):
                db_manage.add_user(user_id, first_name, last_name,
                                   city, age, gender)

            if text not in ['поиск', 'далее', 'в избранное', 'избранное']:
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Поиск')
                keyboard.add_button('Избранное')

                message = f'Добро пожаловать в Vkinder \n' \
                          f'Для поиска людей нажмите кнопку "Поиск" \n' \
                          f'Показать избранное - кнопка "Избранное"'

                send_message(user_id, message, keyboard)

            if text in ['поиск', 'далее']:

                vk_manage.offset = db_manage.offset(user_id)
                rel_id = vk_manage.get_relationship(gender, city, age)

                vk_id, vk_link, first_name, last_name, \
                    gender, city, age = vk_manage.gets_client(rel_id)

                while db_manage.check_history(user_id, rel_id):
                    db_manage.update_offset(user_id)
                    time.sleep(0.35)

                    vk_manage.offset = db_manage.offset(user_id)
                    rel_id = vk_manage.get_relationship(gender, city, age)

                    vk_id, vk_link, first_name, last_name, \
                        gender, city, age = vk_manage.gets_client(rel_id)

                db_manage.update_offset(user_id)

                message = ' '.join([first_name, last_name]) + f' - {vk_link}'

                photos = vk_manage.get_photos(rel_id)
                attchments = []

                for item in photos:
                    image = requests.get(item, stream=True)
                    photo = upload.photo_messages(photos=image.raw)[0]
                    owner_id, id = photo['owner_id'], photo['id']
                    attchments.append(f'photo{owner_id}_{id}')

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Выход')
                keyboard.add_button('Далее')
                keyboard.add_button('В избранное')

                send_message(user_id, message, attachments=attchments,
                             keyboard=keyboard)

                db_manage.add_history(user_id, vk_id)

            elif text == 'в избранное':
                last_id = db_manage.last_histoty(user_id)

                vk_id, vk_link, first_name, last_name, \
                    gender, city, age = vk_manage.gets_client(last_id)

                photos = vk_manage.get_photos(last_id)
                attchments = []

                for item in photos:
                    image = requests.get(item, stream=True)
                    photo = upload.photo_messages(photos=image.raw)[0]
                    owner_id, id = photo['owner_id'], photo['id']
                    attchments.append(f'photo{owner_id}_{id}')

                db_manage.add_favourites(user_id, first_name, last_name,
                                         vk_link, attchments)

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Выход')
                keyboard.add_button('Далее')

                message = f'{first_name} {last_name} добавлен(а) в избранное.'

                send_message(user_id, message, keyboard=keyboard)

            elif text == 'избранное':
                favourites_list, photo_list = db_manage.show_favourites(
                    user_id)

                for favorites, attchments in zip(favourites_list, photo_list):
                    first_name, last_name, vk_link = favorites[1:4]

                    message = ' '.join(
                        [first_name, last_name]) + f' - {vk_link}'

                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Выход')
                    send_message(user_id, message, attachments=attchments,
                                 keyboard=keyboard)
