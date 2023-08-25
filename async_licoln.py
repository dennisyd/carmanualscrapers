import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio


ALL = []


async def get_manuals_links(js, year, model):
    if not js['getOwnerInformationByYearModelResult']['ownerServiceResult']:
        print( year, model) # manual sanity check later 
    for i in js['getOwnerInformationByYearModelResult']['ownerServiceResult']:
        for j in i['matches']['item']:
            if j['category'] == 'Owner’s Manual':
                yield j['link']


def get_all_links():
    url = 'https://www.lincoln.com/support/owner-manuals/owner-manuals-sitemap/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='html.parser')
    div = soup.find_all('div',class_='fds-segmented-control__panel-content')[-1]
    for i in div.find_all('div',class_='accordion-description'):
        for j in i.find_all('a'):
            yield i['id'], j.text


async def fetch_manuals(session, year, model):
    print(f"fetching manuals for {year} {model}")
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'Connection': 'keep-alive',
        'Origin': 'https://www.lincoln.com',
        'Referer': 'https://www.lincoln.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    params = {
        'country':'USA',
        'language':'EN-US',
        'model':model,
        'year':year
    }
    async with session.get('https://www.digitalservices.ford.com/pts/api/v2/owner-information-model-year', params= params, headers=headers) as response:
        data = await response.json()
        async for j in get_manuals_links(data, year, model):
            ALL.append(j)

async def main():
    models = list(get_all_links())  # Convert to a list to prevent multiple iteration
    async with aiohttp.ClientSession() as session:
        tasks = []
        for year, model in models:
                task = asyncio.create_task(fetch_manuals(session, year, model))
                tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    with open('lincoln\manuals_lincoln.txt', 'w') as f:
        f.write('\n'.join(list(set(ALL))))