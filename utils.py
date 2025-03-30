import httpx
import re
from bs4 import BeautifulSoup
import asyncio


async def yd_ids(url: str, login: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post('https://adm.yadonor.ru/index.php?obj=BLOOD_STATIONS', data={'login': login, 'password': password})
           # TODO: добавить проверку ту ли ссылку нам пихнули
        params_url = url.split('?')[1]
        station_id = ''
        for param in params_url.split('&'):
            if param.split('=')[0] == 'BLOOD_STATIONS_ID':
                station_id = param.split('=')[1]
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup = soup.find_all(attrs={'name': re.compile('reserv')})
        groups = []
        for block in soup:
            if block.get('name')[7:10] not in groups:
                groups.append(block.get('name')[7:10])
        # print(groups)
        ready_groups = [groups[0], groups[4], groups[1], groups[5], groups[2], groups[6], groups[3], groups[7]]
        return ready_groups, station_id

async def main():
    await yd_ids('https://adm.yadonor.ru//index.php?obj=BLOOD_STATIONS&action=change&BLOOD_STATIONS_ID=1127&from=1&sort_field=LIST_ORDER&sort_ord=asc&prev_params=YToxOntzOjM6Im9iaiI7czoxNDoiQkxPT0RfU1RBVElPTlMiO30%3D',
                 'xxxxx',
                 'xxxxx')

asyncio.run(main())