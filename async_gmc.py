import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio


ALL = []

def get_all_models(year):
    response = requests.get(
        f'https://www.gmc.com/bypass/pcf/gma-search-api/searchapi/solr/make-model-year/select?facet.field=make_en&facet=on&q=year%3A{year}%20AND%20region%3AGMNA%20AND%20(country%3AUS%20OR%20(*%3A*%20NOT%20country%3A*))&rows=1000',

    )
    x = []
    for i in response.json()['response']['docs']:
        x.append((i['model_en'], i['year'],i['make_en']))

    yield from list(set(x))

async def fetch_manuals(session, model, year, make):
    url = f"https://www.gmc.com/bypass/pcf/gma-search-api/searchapi/solr/gma-public/select?defType%3Dedismax%26fl%3Dimdocid%2Cimcontent_text_id%2Cpath%2Ctitle_ordered%2Ccategory_key%2Cfile_type%26fq%3Dchannel%3AMANUALS%26fq%3Dfile_type%3Aapplication%2Fpdf%26fq%3Dlocale%3Aen_US%26q%3D%2B{year}%20%2B{make}%20%2B{model}%26rows%3D15%26qf%3Dtitle_en%5E200.0%20title_es%5E200%20title_ar%5E200%20title_pt%5E200%20title_ru%5E200%20title_th%5E200%20title_fr%5E200%20title_ko%5E200%20category_translated%5E150.0%20category_translated_path%5E120.0%20category_key_path%5E90.0%20mmy%5E80.0%20category_key%5E75%26stopwords%3Dtrue%26useParams%3Ddefault"

    async with session.get(url) as response:
        data = await response.json()
        for i in data['response']['docs']:
            print(i['path'], year, model, make) 
            ALL.append('https://www.gmc.com/bypass/pcf/gma-content-api'+i['path'])

async def main():
    async with aiohttp.ClientSession(cookies=None) as session:
        for year in list(range(1993,2025)):
            print(f"Scraping Year {year}")
            tasks = []
            for model in get_all_models(year):

                task = asyncio.create_task(fetch_manuals(session, *model))
                tasks.append(task)
            await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    with open('gmc\manuals_gmc.txt', 'w') as f:
        f.write('\n'.join(list(set(ALL))))