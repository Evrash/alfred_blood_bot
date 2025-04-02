import httpx
import re
from bs4 import BeautifulSoup
import asyncio
import base64

from vkbottle import API


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
                groups = [x for x in range(n_first, n_first + 8)]
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


def make_message(yellow_string, red_string, org=None):
    message_str = ''
    if not yellow_string and not red_string:
        message_str = 'Уважаемые доноры, сегодня: \n' \
                      'Всех групп достаточно!'
    else:
        if org and org.start_text:
            message_str = org.start_text + '\n'
        else:
            message_str = 'Уважаемые доноры, на сегодняшний день наш «Донорский светофор» выглядит следующим образом:\n'
        if yellow_string:
            message_str += 'Недостаточно крови: ' + sorted_string(yellow_string) + ' группы\n'
        if red_string:
            message_str += 'Острая нехватка крови: ' + sorted_string(red_string) + ' группы\n'
        if org and org.end_text:
            message_str += org.end_text
        else:
            message_str += ('Ждем доноров на кроводачу (не плазму⛔) без предварительной записи '
                            '(возможность сдачи Вами крови '
                            'рекомендуем уточнить по телефону 286-013)')
    return message_str


async def get_vk_group_name():
    api = API('')

    r = await api.groups.get_by_id()
    print(r)


async def main():
    await get_vk_group_name()

asyncio.run(main())