import os
import vk_api
from dotenv import load_dotenv
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vkinder_db.work_with_db import Database, connect_db
from vkinder_db.model_db import create_tables
from vk_user import VkUser
from message import Message

if __name__ == '__main__':

    load_dotenv()
    group_token = os.environ['vk_group_token']
    user_token = os.environ['vk_bot_token']
    db_password = os.environ['db_pass']

    vk_session = vk_api.VkApi(token=group_token)
    vk = vk_session.get_api()

    upload = VkUpload(vk_session)
    longpoll = VkLongPoll(vk_session)

    vk_manage = VkUser(group_token, user_token)
    message = Message(vk_session)

    session, engine = connect_db(db_password)
    db_manage = Database(session)
    create_tables(engine)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text.lower()
            user_id = event.user_id
            key = str(user_id)

            if str(user_id) not in vk_manage.rel_dict:
                vk_user_id, vk_link, first_name, last_name, \
                    gender, city, age = vk_manage.gets_client(user_id)

                db_manage.add_user(vk_user_id, first_name,
                                   last_name, city, age, gender)

                vk_manage.rel_dict[str(user_id)] = \
                    vk_manage.rel_search(gender, city, age)


            if text not in ['поиск', 'далее', 'в избранное', 'избранное']:
                message.hello(user_id)

            if text in ['поиск', 'далее']:
                rel_id = vk_manage.rel_dict[key].pop(0)

                first_name, last_name, vk_link = vk_manage.rel_info(rel_id)

                photos = vk_manage.get_photos(rel_id, upload)

                messages = ' '.join([first_name, last_name]) + f' - {vk_link}'
                message.next(user_id, messages, photos)

                db_manage.add_history(user_id, rel_id)

            elif text == 'в избранное':

                last_id = db_manage.last_histoty(user_id)

                vk_id, vk_link, first_name, last_name, \
                    gender, city, age = vk_manage.gets_client(last_id)

                messages = f'{first_name} {last_name} добавлен(а) в избранное.'
                message.add_favourites(user_id, messages)

                photos = vk_manage.get_photos(last_id, upload)

                db_manage.add_favourites(user_id, first_name, last_name,
                                         vk_link, photos)

            elif text == 'избранное':
                favourites_list, photo_list = db_manage.show_favourites(user_id)

                message.show_favourites(user_id, favourites_list, photo_list)



