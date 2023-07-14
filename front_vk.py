#from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from back_vk import VkTools
from config import group_token, acces_token

from b_d import Viewed, add_user, check_user, engine


class BotInterface():


    def __init__(self, group_token, acces_token):
        self.vk = vk_api.VkApi(token=group_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                if event.text.lower() == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["name"]}!')

                    # запрос отсутствующего
                    if self.params['year'] is None:
                        self.message_send(event.user_id, f'Укажите возраст')
                        age = (self.event_info())

                    if self.params['city'] is None:
                        self.message_send(event.user_id, f'Укажите город')
                        self.params['city'] = (self.event_info())

                elif event.text.lower() == 'поиск':
                        # логика для поиска анкет
                    self.message_send(event.user_id, 'Идёт поиск')
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 10

                    self.message_send(event.user_id,
                                        f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',
                                        attachment=photo_string)

                    if not check_user(engine, event.user_id, worksheet["id"]):
                        add_user(engine, event.user_id, worksheet["id"])


                elif event.text.lower() == 'пока':
                    self.message_send(event.user_id, 'До новых встреч')

                else:
                    self.message_send(event.user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot_interface = BotInterface(group_token, acces_token)
    bot_interface.event_handler()