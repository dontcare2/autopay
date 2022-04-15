import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sys, json
from vk_api.utils import get_random_id
from threading import Thread
from time import sleep
from me_class import *
# инициализация сессии #
vkBot = Bot(token='a1619d5400b0b5b215bea7b7186700a143f6538a80c9929f958cfff338cbb134f7bb756717414ee495d64')
##################################
# инициализация констант #
myId, mainChatId, sitisChatId, gildChatId, transferBotId = 246960404, 2000000064, 2000000070, 2000000076, -183040898
sleepMode = True
autoPostMessage = '.'
items = {}
msgToPay = None
##################################

def autopost():
    while True:
        if sleepMode is True:
            sleep(1)
            continue
        try:
            vkBot.send(sitisChatId, autoPostMessage)
        except:
            vkBot.send(myId, 'Автопост в ситис ошибка')
        try:
            vkBot.send(mainChatId, autoPostMessage)
        except:
            vkBot.send(myId, 'Автопост в мейн ошибка')
        sleep(1800)


def reply_or_fwd(msg):
    i = vkBot.getByMsgId(msg.message_id)
    if i.get('reply_message'):
        return i['reply_message']
    elif i.get('fwd_messages'):
        return i['fwd_messages'][0]
    else:
        return None


def get_id(text):
    num = 0
    for i in range(0, len(text)):
        if text[i] != '|':
            num = num * 10 + int(text[i])
        else:
            break
    return num


def check_item_and_pay(msg):
    text = msg.text.lower()
    item = text[(text.find(":") + 3):(len(text) - text[::-1].find(":") - 1)]
    mult = 1

    if item.find("*") != -1:
        mult = int(item[:item.find("*")])
        item = item[item.find("*") + 1:]
    if items.get(item) is None:
        return

    price, currency = items[item]
    payment = mult * price
    personId = get_id(text[text.find("[") + 3:])
    if msgToPay is not None and personId == msgToPay.user_id:
        id = msgToPay.message_id
        vkBot.send(msgToPay.peer_id, 'Передать ' + str(payment) + ' ' + currency, id)
        vkBot.send(myId, 'Заплачено ' + str(payment) + ' ' + currency + ' за ' + str(mult) + ' ' + item)


autoPostThread = Thread(target=autopost, daemon=True)
autoPostThread.start()

def main():
    global sleepMode, autoPostMessage, items, myId, sitisChatId, mainChatId, msgToPay
    while True:
        try:
            for msg in vkBot.listen():
                if msg.from_chat or msg.from_user or msg.from_group:
                    msg_id = msg.message_id
                    data = vkBot.getByMsgId(msg_id)
                    conv_id = data['conversation_message_id']
                    text = msg.text.lower()
                    # Диалог с собой - настройка
                    if msg.to_me is True and msg.from_user is True and msg.user_id == myId:
                        if text == 'пп':
                            vkBot.send(msg.peer_id, 'Жив')
                        if text == 'стартспам':
                            sleepMode = False
                        if text == 'не спамим':
                            sleepMode = True
                        if text == 'выкл':
                            ####
                            pass
                        if text.split()[0] == 'объявление':
                            autoPostMessage = msg.text[10:]
                            vkBot.send(msg.peer_id, 'Текст обновлен')
                        if text.split()[0] == 'предмет':
                            try:
                                s = text.split()
                                price = int(s[1])
                                currency = s[2]
                                item = ''
                                for i in range(3, len(s)):
                                    item += ' ' + s[i]
                                item = item.replace(' ', '', 1)
                                if items.get(item) is None:
                                    items[item] = price, currency
                                    vkBot.send(msg.peer_id, item + ' добавлен')
                                else:
                                    items[item] = price, currency
                                    vkBot.send(msg.peer_id, item + ' обновлен')
                            except:
                                vkBot.send(msg.peer_id, 'Ошибка')
                                continue
                        if text.split()[0] == 'удали':
                            item = text[6:]
                            if items.get(item) is None:
                                vkBot.send(msg.peer_id, item + ' не найдено')
                            else:
                                items.pop(item)
                                vkBot.send(msg.peer_id, item + ' удалено')
                    # Взаимодействие с чатами для оплаты если бот не в спящем режиме#
                    if sleepMode is not True and (msg.peer_id == mainChatId or msg.peer_id == sitisChatId or msg.from_group):
                        if text.find('передать') != -1 and reply_or_fwd(msg) is not None \
                                and reply_or_fwd(msg)['from_id'] == myId:
                            msgToPay = msg
                        if msg.from_group \
                                and len(text) > 8 \
                                and text[:8] == 'получено':
                            check_item_and_pay(msg)
        except TypeError:
            print('Была ошибка в лонгполе')
        except IndexError:
            print('Была ошибка в reply_or_forward')
        except:
            print('Другая ошибка')


mainThread = Thread(target=main, daemon=True)
mainThread.start()
mainThread.join()