#!/usr/bin/python3

import time
from typing import Dict, List
import json
import logging
import requests
import math

import discord
import environ

logger = logging.getLogger(__name__)

root_env = environ.Env()
root_env.read_env()

hf_env = environ.Env()
hf_env.read_env("heckguide/.env")

hf_token = hf_env("TOKEN")
hf_staytoken = hf_env("STAY_TOKEN")

discord_token = root_env("DISCORD_TOKEN")

NOTIFY_TITAN = hf_env("NOTIFY_TITAN")
if NOTIFY_TITAN == "False":
    NOTIFY_TITAN = False
else:
    NOTIFY_TITAN = True

# In seconds
REQUEST_TIMEOUT = 5


class TokenException(Exception):
    """Empty class"""


class Point:
    """Point holder"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def return_segment(self):
        """Returns the closest segment"""
        # 512,0 X,Y -> 64
        # 0,1024 X,Y -> 8192
        x = math.ceil(self.x / 8)
        x = x * 8
        y = math.ceil(self.y / 64)
        y = y * 64

        segment = int((x + y * 64) / 8)

        return segment

    def __lt__(self, other):
        if self.x < other.x and self.y < other.y:
            return True
        return False

    def __gt__(self, other):
        if self.x > other.x and self.y > other.y:
            return True
        return False

    def __le__(self, other):
        if self.x <= other.x and self.y <= other.y:
            return True
        return False

    def __ge__(self, other):
        if self.x >= other.x and self.y >= other.y:
            return True
        return False


class HFAPI:
    """Wrapper for HF API"""

    def __init__(self):
        self.base_url = "https://api.kingdomsofheckfire.com"
        self.token = hf_token
        self.staytoken = hf_staytoken
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    async def _post(self, url: str, data: Dict) -> Dict:
        """Standarized POST request"""
        response = requests.post(
            url, headers=self.headers, data=data, timeout=REQUEST_TIMEOUT
        )

        json_data = json.loads(response.text)
        if json_data.get("exception"):
            raise TokenException(json_data["exception"])

        return json_data

    async def get_clan_for_user(self):
        """Sends request to api to grab the current clan for logged in user,
        pulls group_id from response"""
        data = {"authorization": f"Bearer {self.token}", "Accept": "application/json"}
        url = f"{self.base_url}/game/group/get_group_for_user/"
        req = requests.get(url, headers=data, timeout=REQUEST_TIMEOUT)
        json_data = json.loads(req.text)

        if "id" not in json_data:
            raise TokenException(
                f"Could not query serverm verify that {self.token=} is valid/assigned"
            )

        group_id = json_data["id"]
        if json_data.get("exception"):
            raise TokenException(json_data["exception"])

        return group_id

    async def message_clan(self, message: str) -> Dict:
        """Sends given message to current tokens clan chat"""

        group_id = self.get_clan_for_user()
        url = f"{self.base_url}/game/message/send_group_chat/"
        data = {"group_id": group_id, "message": message}

        return await self._post(url, data)

    async def stay_alive(self):
        """Sends the first and second half of each token to
        the ticket response to keep the token alive."""
        data = {
            "authorization": f"Session {self.staytoken}:{self.token}",
            "Accept": "application/json",
        }
        url = f"{self.base_url}/support/tickets/"
        req = requests.get(url, headers=data, timeout=REQUEST_TIMEOUT)

        try:
            json_data = json.loads(req.text)
        except Exception as exception:
            raise TokenException(exception)

        # print(f"{json_data=}")
        if json_data.get("exception"):
            raise TokenException(json_data["exception"])

        return json_data

    async def get_allies_by_price(self, price: int, limit: int, offset: int) -> Dict:
        """Searches the ally api using max cost and page offset."""
        url = f"{self.base_url}/game/ally/search_allies"
        data = {"max_cost": price, "offset": offset, "limit": limit}
        # print(f"{data=}")

        return await self._post(url, data)

    async def collect_loot(self):
        """Collects any sold ally gold from the treasury."""

        data = {"authorization": f"Bearer {self.token}", "Accept": "application/json"}
        url = f"{self.base_url}/game/resource/collect_unlootable_resources/"
        req = requests.get(url, headers=data, timeout=REQUEST_TIMEOUT)
        json_data = json.loads(req.text)

        if json_data.get("exception"):
            raise TokenException(json_data["exception"])

        return json_data

    async def find_ally(self, user, price, page_count, start_count):
        price = int(price.replace(",", ""))
        page_count = int(page_count)
        limit = 50
        start_count = int(start_count)

        await user.send(
            "Starting ally crawler for price: "
            f"{price:,} with page count: {page_count} "
            f"with start_page: {start_count}"
        )

        lowest_price = -1
        highest = {"total": 0, "price": 0}
        last_username = None
        sleep_time = 30
        not_found = 0
        for i in range(limit * start_count, limit * (start_count + page_count), limit):
            data = {"allies": []}
            while True:
                # Loop if the exception occured (so we don't skip)
                try:
                    await user.send(
                        f"Page count: {i} out of {limit*(start_count+page_count)}"
                    )
                    data = await self.get_allies_by_price(
                        price=price, limit=limit, offset=i
                    )
                except TokenException as exception:
                    await user.send(
                        "find_ally - Token exception found\n"
                        f"Sleeping for {sleep_time} seconds before retry.\n"
                        f"Exception: {exception}"
                    )
                    time.sleep(sleep_time)
                break

            allies = data["allies"]
            if len(allies) != limit:
                await user.send(
                    f"WARNING: Allies count: {len(allies)} smaller than {limit=}, {not_found=}"
                )
                not_found += 1
            else:
                not_found = 0

            if not_found > 5:
                # Stop if 5 searches returned nothing
                break

            for ally in allies:
                if lowest_price == -1:
                    lowest_price = ally["cost"]

                if lowest_price > ally["cost"]:
                    lowest_price = ally["cost"]

                total = (
                    ally["biome3_attack_multiplier"]
                    + ally["biome4_attack_multiplier"]
                    + ally["biome5_attack_multiplier"]
                ) / 100.0

                if highest["total"] < total:
                    highest["g"] = ally["biome3_attack_multiplier"] / 100.0
                    highest["b"] = ally["biome4_attack_multiplier"] / 100.0
                    highest["s"] = ally["biome5_attack_multiplier"] / 100.0
                    highest["price"] = ally["cost"]
                    highest["username"] = ally["username"]
                    highest["total"] = total
                    # print(f"{highest['username']} with {total=}")

            if "username" in highest:
                # Make sure the item is set

                if last_username is None or last_username != highest["username"]:
                    await user.send(
                        f"'{highest['username']}' with {highest['total']=} "
                        f"for {highest['price']=:,}"
                    )
                    await user.send(f'{highest["g"]} / {highest["b"]} / {highest["s"]}')

                last_username = highest["username"]

        await user.send(f"Lowest price: {lowest_price:,}")

        if "username" in highest:
            # Make sure the item is set
            await user.send(f"Final verdict {highest=}")

        stay_alive = await self.stay_alive()
        if "timestamp" not in stay_alive:
            print(f"EXCEPTION occured: {stay_alive['detail']}")
        else:
            logger.info("Keeping token alive: %d", stay_alive["timestamp"])

        logger.info("Collecting Loot")
        await self.collect_loot()
        logger.info("Done")

        return highest

    async def fetch_world(self, sgement: int):
        """
        Fetches up to 20 chunks of world map data only taking the 'sites' chunk of response.
        NOTE: 20 is the api limit.
        """
        tiles = []
        url = f"{self.base_url}/game/nonessential/poll_segments_realm_state"
        # data = {"segment_ids": [i for i in range(lowerbound, lowerbound + 20)]}
        data = {"segment_ids": [sgement]}

        req = requests.post(
            url, headers=self.headers, data=data, timeout=REQUEST_TIMEOUT
        )
        json_data = req.json()

        if "world_state" not in json_data:
            raise TokenException(
                f"Could not query serverm verify that {self.token=} is valid/assigned"
            )

        sites = json_data["world_state"]["sites"]
        for tile in sites:
            tiles.append(sites[tile])

        data["segment_ids"] = [d + 20 for d in data["segment_ids"]]

        return tiles


class BotMain(discord.Client):
    """Main functionality of Bot"""

    async def on_ready(self):
        """Inform people we are ready"""
        print("Logged on as", self.user)

    async def help(self, content, user):
        """Help me..."""

        supported = {
            "find_ally": {"parameters": ["price", "page_count", "start_count"]},
            "crawl_world": {"parameters": []},
        }

        items = content.split(" ")
        if len(items) == 1:
            await user.send("Help")
            for (cmd, cmd_item) in supported.items():
                await user.send(f"*{cmd}* - parameters: {cmd_item['parameters']}")

    async def crawl_world(self, _, user):
        """Crawl a given map"""

        # X:0, Y:0 is segment 0
        # X:511, Y:0 is segment 63
        # X:511, Y:1022 is segment 8191
        # X:0, Y:1022 is segment 8128
        # So every line has 64 segments (0..63)
        # Every segment has 512 squares in it
        # Square bottom left, 209:464, top left, 210:560
        # Square top right: 301:554, bottom right: 301:464
        # (X + Y * 512) / 64 => Segment
        # (209+464*512)/64 -> 3714
        # (301+464*512)/64 -> 3718
        # (210+560*512)/64 -> 4483
        # (301+554*512)/64 -> 4436

        # Titan 5 284:496, 291:511

        lowerbound = Point(200, 460)
        upperbound = Point(310, 560)
        current_position = Point(lowerbound.x, lowerbound.y)

        api_endpoint = HFAPI()
        await user.send("Starting to crawl")

        while True:
            segments = []
            while True:
                try:
                    await user.send(f"{current_position.return_segment()=}")
                    segments = await api_endpoint.fetch_world(
                        current_position.return_segment()
                    )
                except TokenException as exception:
                    await user.send(
                        f"Token exception found, sleeping for 60 seconds before retry. "
                        f"Exception: {exception}"
                    )

                    time.sleep(60)

                break

            await user.send(f"Found {len(segments)} segments")
            for (idx, segment) in enumerate(segments):
                if idx == 0:
                    await user.send(
                        f'X: {segment["x"]} '
                        f'Y: {segment["y"]} <- {lowerbound.return_segment()}'
                    )

                # if segment["owner_username"]:
                #     await user.send(
                #         f'Found player: {segment["owner_username"]}, '
                #         f'Clan: {segment["owner_group_name"]}'
                #     )

                if "Titan [Lv" in segment["name"]:
                    await user.send(
                        f'{segment["name"]} X: {segment["x"]} Y: {segment["y"]}'
                    )

                    # if NOTIFY_TITAN:
                    #     api_endpoint.message_clan(
                    #         f"{segment['name']} X: {segment['x']} Y: {segment['y']}"
                    #     )

            current_position.x += 8
            if current_position.x > upperbound.x:
                await user.send("Rolling back to the left")
                current_position.x = lowerbound.x
                current_position.y += 8

            if current_position.y > upperbound.y:
                await user.send("Done inside loop")
                break

            stay_alive = await api_endpoint.stay_alive()
            if "timestamp" not in stay_alive:
                print(f"EXCEPTION occured: {stay_alive['detail']}")
            else:
                print(f"Keeping token alive: {stay_alive['timestamp']}")

            logger.info("Collecting Loot")
            await api_endpoint.collect_loot()
            logger.info("Done")

        await user.send("Done loop")

    async def find_ally(self, content, user):
        """Find me an ally"""
        items = content.split(" ")
        price = 100
        page_count = 10
        start_count = 0

        if len(items) > 1:
            price = items[1]
        if len(items) > 2:
            page_count = items[2]
        if len(items) > 3:
            start_count = items[3]

        await user.send(f"find_ally(message, {price=}, {page_count=}, {start_count=})")

        api_endpoint = HFAPI()
        await api_endpoint.find_ally(user, price, page_count, start_count)
        # await message.reply(f"{highest=}")

    async def on_message(self, message):
        """Message handler"""

        # don't respond to ourselves
        if message.author == self.user:
            return

        user = await client.fetch_user(message.author.id)

        content: str = message.clean_content

        if message.clean_content != message.content:
            # It means there is a mention there.. clean it
            space = content.find(" ")
            if space is not None:
                content = content[space + 1 :]

        print(f"{content=}")
        if content.startswith("help"):
            await self.help(content, user)
        elif content.startswith("crawl_world"):
            await self.crawl_world(content, user)
        elif content.startswith("find_ally"):
            await self.find_ally(content, user)
        elif content == "ping":
            await message.reply("pong")
        else:
            await message.reply("Unknown command", mention_author=True)


# intents = discord.Intents.default()
intents = discord.Intents.all()

client = BotMain(intents=intents)

client.run(discord_token)
