import httpx
import re
from bs4 import BeautifulSoup
# import asyncio
import base64
from cryptography.fernet import Fernet
from vkbottle import API, VKAPIError, PhotoWallUploader

import config
from config import settings


def check_key():
    key_file = settings.base_dir / '.key'
    if not key_file.is_file():
        key = Fernet.generate_key()
        with open(settings.base_dir / '.key', 'wb+') as f:
            f.write(key)


def encode_str(string):
    key_file = settings.base_dir / '.key'
    key = key_file.read_bytes()
    cipher = Fernet(key)
    return cipher.encrypt(string.encode('utf-8'))


def decode_str(string):
    key_file = settings.base_dir / '.key'
    key = key_file.read_bytes()
    cipher = Fernet(key)
    return cipher.decrypt(string).decode('utf-8')


async def yd_ids(url: str, login: str, password: str):
    """
    Получение списка Id групп, Id станции, флага успешной авторизации
    :param url: адрес страницы со светофором
    :param login: логин YD
    :param password: пароль YD
    :return: (список групп, Id станции, флаг пользователя)
    """
    async with httpx.AsyncClient() as client:
        response = await client.post('https://adm.yadonor.ru/index.php?obj=BLOOD_STATIONS', data={'login': login, 'password': password})
           # TODO: добавить проверку ту ли ссылку нам пихнули
        print(response)
        if response.status_code == 302:
            is_user = True
        else:
            is_user = False
        params_url = url.split('?')[1]
        station_id = ''
        for param in params_url.split('&'):
            if param.split('=')[0] == 'BLOOD_STATIONS_ID':
                station_id = param.split('=')[1]
            if param.split('=')[0] == 'BLOOD_RESERVE_ID':
                n_first = int(param.split('=')[1])
                groups = [str(x) for x in range(n_first, n_first + 8)]
        print(groups, station_id, is_user)
        return groups, station_id, is_user


def make_message(light: dict[str:str], start_text: str=None, end_text: str = None, hashtag:str = None):
    """
    Формирование сообщение для светофора
    :param light: Шаблон готового светофора
    :param start_text: Начальный текст
    :param end_text: Конечный текст
    :param hashtag: Хэштеги
    :return: Строка с готовым текстом для светофора
    """
    message_str = ''
    if not any(x in light.values() for x in ['yellow', 'red']):
        message_str = 'Уважаемые доноры, сегодня: \nВсех групп достаточно!'

    else:

        if start_text:
            message_str = f'{start_text}\n'
        else:
            message_str = 'Уважаемые доноры, на сегодняшний день наш «Донорский светофор» выглядит следующим образом:\n'
        yellow_str = ''
        red_str = ''
        for group, value in light.items():
            if value == 'yellow':
                yellow_str += f'{settings.group.__getattribute__(group)}, '
            if value == 'red':
                red_str += f'{settings.group.__getattribute__(group)}, '
        if yellow_str:
            # message_str += f'Есть потребность:\n🟡 {yellow_str.rstrip(', ')}\n'
            message_str += f'Есть потребность:\n{'\n'.join(f'🟡 {x}' for x in yellow_str.rstrip(', ').split(', '))}\n'
        if red_str:
            # message_str += f'Повышенная потребность:\n🔴 {red_str.rstrip(', ')}\n'
            message_str += f'Повышенная потребность:\n{'\n'.join(f'🔴 {x}' for x in red_str.rstrip(', ').split(', '))}\n'
        if end_text:
            message_str += f'{end_text}\n'
        else:
            message_str += ('Ждем доноров на кроводачу (не плазму⛔) без предварительной записи '
                            '(возможность сдачи Вами крови '
                            'рекомендуем уточнить по телефону 286-013)\n')
    if hashtag:
        message_str += f'{hashtag}\n'
    return message_str


async def get_vk_group_id(token:str, group_link: str):
    """
    Получение ID группы в ВК с помощью vkbottle
    :param token: ВК токен
    :param group_link: Ссылка на группу
    :return: Словарь содержащий либо группу, либо ошибку
    """
    group_name = group_link.split('/')[-1]
    api = API(token)
    try:
        r = await api.utils.resolve_screen_name(screen_name=group_name)
    except (VKAPIError[1116], VKAPIError[5]) as e:
        print('Ошибка авторизации')
        return {'error_msg': 'Не верный токен'}
    except VKAPIError as e:
        print(e.error_msg, e.code)
        return {'error_msg': f'Неизвестная ошибка: error:{e.error_msg}, code:{e.code}'}
    else:
        return {'group_id': int(r.object_id)}


async def publish_to_yd(login, password, station_id, group_ids, group_vals):
    """
    Публикация светофора на YD
    :param login: Логин пользователя
    :param password: Пароль пользователя
    :param station_id: ID станции
    :param group_ids: Список ID групп
    :param group_vals: Список значений групп
    :return: None
    """
    groups = ['reserv[' + x + ']' for x in group_ids.split(',')]
    blood_reserve_id = group_ids.split(',')[0]
    vals = group_vals.split(',')
    yd_data = dict(zip(groups, vals))
    yd_data['spk_id'] = station_id
    async with httpx.AsyncClient() as client:
        #TODO: добавить try
        await client.post('https://adm.yadonor.ru/index.php?obj=BLOOD_STATIONS',
                          data={'login': login, 'password': password})
        # TODO: Исправть reservid
        r = await client.post(f'https://adm.yadonor.ru/index.php?obj=BLOOD_RESERVE&action=change&BLOOD_RESERVE_ID={blood_reserve_id}&BLOOD_STATIONS_ID={station_id}'
                          , data=yd_data)
        print(r.request)

async def publish_to_vk(vk_token: str, org_dir: str, image_name: str, group_id: int, text: str, is_pin: bool =True,
                        prev_post_id: int=None, is_del_post: bool=True):
    """
    Публикация светофора и сообщения в VK
    :param vk_token: Токен ВК
    :param org_dir: Директория расположения картинки
    :param image_name: Имя файла картинки
    :param group_id: ID группы в ВК
    :param text: Текст сообщения
    :param is_pin: Флаг необходимости закрепления светофора на стене
    :param prev_post_id: ID предыдущего поста для удаления
    :return:
    """
    api = API(vk_token)
    try:
        if prev_post_id and is_del_post:
            await api.wall.delete(owner_id=-group_id, post_id=prev_post_id)
        photo_uploader = PhotoWallUploader(api)
        img_path = config.BASE_DIR / 'img' / org_dir / image_name
        photo = await photo_uploader.upload(file_source=str(img_path), group_id=group_id)
        post_response = await api.wall.post(owner_id=-group_id, from_group=True, message=text, attachments=[photo])
        print(post_response)
        if is_pin:
            await api.wall.pin(owner_id=-group_id, post_id=post_response.post_id)
    except (VKAPIError[1116], VKAPIError[5]) as e:
        print('Ошибка авторизации')
        return {'error_msg': 'Не верный токен'}
    except VKAPIError as e:
        print(e.error_msg, e.code)
        return {'error_msg': f'Неизвестная ошибка: error:{e.error_msg}, code:{e.code}'}
    else:
        return {'post_id': post_response.post_id}
