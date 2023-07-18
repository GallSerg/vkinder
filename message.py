import os
import time
import requests
import vk_api
from dotenv import load_dotenv
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from vkinder_db.model_db import create_tables
from vkinder_db.work_with_db import Database, connect_db
from vk_user import VkUser


class Message():
    def __init__(self, vk_session):
        self.vk_session = vk_session

    def hello(self, user_id):

        message = 'Добро пожаловать в Vkinder\n Для поиска людей нажмите \
                  кнопку "Поиск" \n Показать избранное - кнопка "Избранное"'

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Поиск')
        keyboard.add_button('Избранное')

        param = {'user_id': user_id, 'random_id': get_random_id(),
                 'message': message, 'keyboard': keyboard.get_keyboard()}

        self.vk_session.method('messages.send', param)

    def next(self, user_id, message, attachments):

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Выход')
        keyboard.add_button('Далее')
        keyboard.add_button('В избранное')

        param = {'user_id': user_id, 'random_id': get_random_id(),
                 'message': message, 'keyboard': keyboard.get_keyboard(),
                 'attachment': ','.join(attachments)}

        self.vk_session.method('messages.send', param)

    def add_favourites(self, user_id, message):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Выход')
        keyboard.add_button('Далее')

        param = {'user_id': user_id, 'random_id': get_random_id(),
                 'message': message, 'keyboard': keyboard.get_keyboard()}

        self.vk_session.method('messages.send', param)

    def show_favourites(self, user_id, favourites_list, photo_list):

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Выход')

        for favorites, attachments in zip(favourites_list, photo_list):
            first_name, last_name, vk_link = favorites[1:4]

            message = ' '.join([first_name, last_name]) + f' - {vk_link}'

            param = {'user_id': user_id, 'random_id': get_random_id(),
                     'message': message, 'keyboard': keyboard.get_keyboard(),
                     'attachment': ','.join(attachments)}

            self.vk_session.method('messages.send', param)