from asyncio import sleep
from bs4 import BeautifulSoup

import requests


async def check_new():
    while True:
        r = requests.get("https://freelance.habr.com/tasks")
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("article", {"class": "task task_list"})
        print(cards[0].prettify())
        for card in cards:
            print(card.find("div", {"class": "task__title"}).get('title'))
        await sleep(60)

if __name__ == '__main__':
    import asyncio
    asyncio.run(check_new())

