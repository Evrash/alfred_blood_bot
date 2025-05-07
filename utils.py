import httpx
import re
from bs4 import BeautifulSoup
# import asyncio
import base64

from vkbottle import API, VKAPIError, PhotoWallUploader

import config
from config import settings


def encode_str(string):
    return str(base64.b64encode(string.encode('utf-8')), 'utf-8')


def decode_str(string):
    return base64.b64decode(string).decode('utf-8')


async def yd_ids(url: str, login: str, password: str):
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
        # response = await client.get(url)
        # print(response.text)
        # soup = BeautifulSoup(response.text, 'html.parser')
        # soup = soup.find_all(attrs={'name': re.compile('reserv')})
        # groups = []
        # for block in soup:
        #     if block.get('name')[7:10] not in groups:
        #         groups.append(block.get('name')[7:10])
        # print(groups)
        # ready_groups = [groups[0], groups[4], groups[1], groups[5], groups[2], groups[6], groups[3], groups[7]]
        print(groups, station_id, is_user)
        return groups, station_id, is_user


def sorted_string(line: str) -> str:
    group_list = line.strip().split(',')
    group_list.sort()
    return ', '.join(group_list)


def make_message(light: dict[str:str], start_text: str=None, end_text: str = None, hashtag:str = None):
    def get_text_from_groups(groups: list):
        if groups:
            return ', '.join(settings.group.__getattribute__(x) for x in groups)
        return ''


    message_str = ''
    if not any(x in light.values() for x in ['yellow', 'red']):
        message_str = 'Уважаемые доноры, сегодня: \nВсех групп достаточно!'

    else:

        if start_text:
            message_str = start_text + '\n'
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
            message_str += f'Недостаточно крови:\n🟡 {yellow_str.rstrip(', ')}\n'
        if red_str:
            message_str += f'Острая нехватка крови:\n🔴 {red_str.rstrip(', ')}\n'
        if end_text:
            message_str += end_text
        else:
            message_str += ('Ждем доноров на кроводачу (не плазму⛔) без предварительной записи '
                            '(возможность сдачи Вами крови '
                            'рекомендуем уточнить по телефону 286-013)\n')
    if hashtag:
        message_str += f'{hashtag}\n'
    return message_str


async def get_vk_group_id(token: str):
    api = API(token)
    try:
        r = await api.groups.get_by_id()
    except (VKAPIError[1116], VKAPIError[5]) as e:
        print('Ошибка авторизации')
        return {'error_msg': 'Не верный токен'}
    except VKAPIError as e:
        print(e.error_msg, e.code)
        return {'error_msg': f'Неизвестная ошибка: error:{e.error_msg}, code:{e.code}'}
    else:
        return {'id': int(r.groups[0].id)}


async def publish_to_yd(login, password, station_id, group_ids, group_vals):
    groups = ['reserv[' + x + ']' for x in group_ids.split(',')]
    vals = group_vals.split(',')
    yd_data = dict(zip(groups, vals))
    yd_data['spk_id'] = station_id
    async with httpx.AsyncClient() as client:
        #TODO: добавить try
        await client.post('https://adm.yadonor.ru/index.php?obj=BLOOD_STATIONS',
                          data={'login': login, 'password': password})
        # TODO: Исправть reservid
        await client.post(f'https://adm.yadonor.ru/index.php?obj=BLOOD_RESERVE&action=change&BLOOD_RESERVE_ID={groups[0]}&BLOOD_STATIONS_ID={station_id}'
                          , data=yd_data)

async def publish_to_vk(vk_token: str, org_dir: str, image_name: str, group_id: int, text: str, is_pin: bool =True,
                        prev_post_id: int=None):
    api = API(vk_token)
    try:
        if prev_post_id:
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



# async def main():
#     res = await get_vk_group_id()
#     print(res)
#     if 'error_msg' in res:
#         print(True)
#
# asyncio.run(main())

# light_template = {'o_plus': 'red', 'o_minus':'green',
#                   'a_plus': 'yellow', 'a_minus':'red',
#                   'b_plus': 'green', 'b_minus':'yellow',
#                   'ab_plus': 'green', 'ab_minus':'red'}
#
# print(make_message(light=light_template))