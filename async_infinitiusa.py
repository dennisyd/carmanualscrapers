import requests
import aiohttp
import asyncio
import json

ALL = []


def get_all_models():
    url = 'https://www.infinitiusa.com/owners/ownership/manuals-guides/_jcr_content/freeEditorial/columns12_55cf/col1-par/manualsandguidessear.tag.json/suffix.html'

    response =  requests.get(url)
    for i in response.json()['applicableVehicles'].values():
        for y in i['years']:
            yield y, i['title']


async def get_manuals(session, year, title):
    url = f"https://www.infinitiusa.com/owners/ownership/manuals-guides/_jcr_content/freeEditorial/columns12_55cf/col1-par/manualsandguidessear.search.json/{title}/{year}/suffix.html"
    async with session.get(url) as response:
        data = await response.text()
        data = json.loads(data)
        for i in data['results']:
            print(i['location'])
            ALL.append('https://www.infinitiusa.com'+i['location'])





async def main():
    async with aiohttp.ClientSession(cookies=None) as session:
        models = list(get_all_models())
        tasks = []
        for model in models:
            task = asyncio.create_task(get_manuals(session, *model))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    with open('infinitiusa\manuals_infinitiusa.txt', 'w') as f:
        f.write('\n'.join(list(set(ALL))))