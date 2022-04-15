from ast import Try
import vk_api
from vk_api.longpoll import *
from vk_api.utils import *
import sqlite3

class Bot(object):
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi (token=token)
        self.longpoll = VkLongPoll (self.vk_session)
        self.vk = self.vk_session.get_api ()
        self.conn = sqlite3.connect('buffs.db')
        self.cur = self.conn.cursor()

    def getByConvID(self, conv, peer):
        result = self.vk_session.method('messages.getByConversationMessageId', {'peer_id': peer,
                                            'conversation_message_ids': conv,
                                            'access_token': self.token
                                            })
        return result['items'][0]

    def listen(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.text.lower():
                        yield event
            except Exception:
                pass


    def getByMsgId(self, id):
        result = self.vk_session.method('messages.getById', {'message_ids': id,
                                        'access_token': self.token
                                        })
        return result['items'][0]

    def send(self, chat, text, reply_id=None):
        result = self.vk_session.method('messages.send', {'peer_id': chat,
                                        'message': text,
                                        'random_id': 0,
                                        'reply_to': reply_id})
        return result