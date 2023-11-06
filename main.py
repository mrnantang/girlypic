import asyncio
import logging
import argparse
from pathlib import Path

import aiohttp
import aiofiles
from lxml import etree

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

PROXY = "http://127.0.0.1:8080"
SAVE_FOLDER = Path("Downloads")
PICTURE_HOST = "https://girlygirlpic.com"
PICTURE_GATHER = PICTURE_HOST + "/ax/"
PICTURE_SEARCH = PICTURE_HOST + "/sx/"
PICTURE_URL = '//div[@class="post-media-body"]//a[@class="figure-link os-lightbox-activator"]/@href'
ALBUM_NAMES = '//div[@class="post-content-body"]/h4[@class="post-title entry-title"]/a[@class="on-popunder"]'
HEADER = {
    "Origin": PICTURE_HOST,
    "Connection": "close",
    "Cookie": "_user_language=Cn",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
}

async def download_picture(url: str, save_folder: Path) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, proxy=PROXY, headers=HEADER) as response:
                picture_name = url[url.rfind("/") + 1:]
                async with aiofiles.open(save_folder / picture_name, "wb") as handle:
                    async for chunk in response.content.iter_chunked(1024):
                        await handle.write(chunk)
        except Exception as exception:
            logger.error(f"{exception} [URL] {url}")

async def parse_album(url: str, save_folder: Path) -> None:
    album_id = url[url.rfind("/") + 1:]
    header = {**HEADER, **{"Referer": url}}
    async with aiohttp.ClientSession() as session:
        requests_body = {"album_id": album_id}
        async with session.post(PICTURE_GATHER, json=requests_body, proxy=PROXY, headers=header) as response:
            html_content = await response.text()
            image_href = etree.HTML(html_content).xpath(PICTURE_URL)
            logger.info(f"{len(image_href):03d} photos of album [{save_folder.name}]")
            task_list = [asyncio.create_task(download_picture(pic_url, save_folder)) for pic_url in image_href]
            await asyncio.wait(task_list) if len(task_list) > 0 else None
            logger.info(f"album saved [{save_folder.name}]")

async def get_albums(name: str) -> None:
    async with aiohttp.ClientSession() as session:
        requests_body = {"search_keys_tag": name}
        async with session.post(PICTURE_SEARCH, json=requests_body, proxy=PROXY, headers=HEADER) as response:
            html_content = await response.text()
            album_content = etree.HTML(html_content).xpath(ALBUM_NAMES)
            logger.info(f"{len(album_content):03d} albums about {name}")
            task_list = []
            for album in album_content:
                href = album.get("href")
                text = album.text
                save_folder = SAVE_FOLDER / name / text
                save_folder.mkdir(parents=True) if not save_folder.exists() else None
                task_list.append(asyncio.create_task(parse_album(href, save_folder)))
            await asyncio.wait(task_list) if len(task_list) > 0 else None

async def main(names: [str]) -> None:
    await asyncio.wait([asyncio.create_task(get_albums(name)) for name in names])
    logger.info("done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="download pictures")
    parser.add_argument("name", type=str, nargs='+', help="girls name list")
    args = parser.parse_args()
    asyncio.run(main(args.name))