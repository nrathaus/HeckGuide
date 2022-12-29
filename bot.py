#!/usr/bin/python3

import time
from typing import Dict, List
import json
import logging
import math

import requests
import discord
import environ

# In seconds
REQUEST_TIMEOUT = 5

def login(username, password) -> str:
    json_data = {
        "bundle_id": "ata.kraken.heckfire",
        "unity_uuid": "817b2a60ae392eb03ed99378ba789acd",
        "os_name": "Android",
        "android_id": "309d26b91717f17c",
        "android_advertising": "dff7bf49-e56f-4ca1-8bf8-676e919f58be",
        "app_set_id": "ba3be074-2eb8-963d-329e-e9650dbbc358",
        "ether_map": {},
        "os_version": "Android OS 12 / API-31 (SP1A.210812.016/A137FXXU1AVH1)",
        "device_model": "SM-A137F",
        "hardware_version": "samsung SM-A137F",
        "limit_ad_tracking": False,
        "screen_width": 1080,
        "screen_height": 2342,
        "locale": "en-GB",
        "os_build": "Build/SP1A.210812.016",
    }

    json_dump = json.dumps(json_data, separators=(",", ":"))

    data = {
        "grant_type": "password",
        "client_version": "2.28.837437069",
        "channel_id": "16",
        "client_id": "ata.kraken.heckfire",
        "client_secret": "n0ts0s3cr3t",
        "scope": "[]",
        "version": "3432",
        "include_tech_tree": False,
        "username" : username,
        "password" : password,
        "client_information": json_dump,
    }

    headers = {
        "User-Agent": "ata bundle_id=ata.kraken.heckfire version=2.28.837437069",
        "Accept": "application/json",
        "Accept-Language": "en-GB",
        "Host": "api.kingdomsofheckfire.com",
    }

    url = "https://api.kingdomsofheckfire.com/game/auth/oauth/"
    response = requests.post(url, data=data, headers=headers, timeout=REQUEST_TIMEOUT)

    json_data = response.json()
    refresh_token = json_data['refresh_token']
    access_token = json_data['access_token']

    return (access_token, refresh_token)

logger = logging.getLogger(__name__)

root_env = environ.Env()
root_env.read_env()

# hf_env = environ.Env()
# hf_env.read_env("heckguide/.env")

hf_username = root_env.get_value("HF_USERNAME", default="")
hf_password = root_env.get_value("HF_PASSWORD", default="")

if hf_username == "" or hf_password == "":
    hf_token = root_env.get_value("TOKEN", default=None)
    hf_staytoken = root_env.get_value("STAY_TOKEN", default=None)
else:
    # User login method
    (hf_token, hf_staytoken) = login(hf_username, hf_password)
    hf_staytoken = "qAF6SgkN5dne0tB2IUwcxf/Ymhb4V9q9KhV+4OftruWUxHYHQAHTJNS4Ld7Z03lXTuDpLOOYy4iNCNp92mV6nw=="

discord_token = root_env("DISCORD_TOKEN")

NOTIFY_TITAN = root_env.get_value("NOTIFY_TITAN", default=True)
if NOTIFY_TITAN == "False":
    NOTIFY_TITAN = False
else:
    NOTIFY_TITAN = True


def divide_chunks(list_items, number):
    """ looping till length l """
    for i in range(0, len(list_items), number):
        yield list_items[i : i + number]


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

    async def fetch_world(self, segment_ids: List[int]):
        """
        Fetches up to 20 chunks of world map data only taking the 'sites' chunk of response.
        NOTE: 20 is the api limit.
        """
        tiles = []
        url = f"{self.base_url}/game/nonessential/poll_segments_realm_state"
        # data = {"segment_ids": [i for i in range(lowerbound, lowerbound + 20)]}
        data = {"segment_ids": segment_ids}

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

        # Relevant segments
        segment_ids = set()
        while True:
            segment_ids.add(current_position.return_segment())

            current_position.x += 8
            if current_position.x > upperbound.x:
                current_position.x = lowerbound.x
                current_position.y += 8

            if current_position.y > upperbound.y:
                break

        segment_ids = list(segment_ids)
        segment_ids.sort()
        # await user.send(f"Relevant segments: {segment_ids}")

        # We need to do this in chunks of 20
        segment_chunks_ids = divide_chunks(segment_ids, 20)

        for segment_chunks_id in segment_chunks_ids:
            segments = []
            while True:
                try:
                    # await user.send(f"{segment_chunks_id=}")
                    segments = await api_endpoint.fetch_world(list(segment_chunks_id))
                except TokenException as exception:
                    await user.send(
                        "crawl_world - Token exception found, sleeping for "
                        "60 seconds before retry. "
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

                # if "Titan Trove" in segment["name"]:
                #     await user.send(
                #         f'{segment["name"]} X: {segment["x"]} Y: {segment["y"]}'
                #     )

                if "Titan [Lv" in segment["name"]:
                    await user.send(
                        f'{segment["name"]} X: {segment["x"]} Y: {segment["y"]}'
                    )

                    # if NOTIFY_TITAN:
                    #     api_endpoint.message_clan(
                    #         f"{segment['name']} X: {segment['x']} Y: {segment['y']}"
                    #     )

            stay_alive = await api_endpoint.stay_alive()
            if "timestamp" not in stay_alive:
                print(f"crawl_world - EXCEPTION occured: {stay_alive['detail']}")
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

        # Make sure we are mentioned
        its_for_me = False
        if len(message.mentions) > 0:
            for mention in message.mentions:
                if mention.id == self.user.id:
                    its_for_me = True
                    break
        else:
            its_for_me = True

        if not its_for_me:
            return

        user = await client.fetch_user(message.author.id)

        content: str = message.clean_content

        if message.clean_content != message.content:
            # It means there is a mention there.. clean it
            space = content.find(" ")
            if space is not None:
                content = content[space + 1 :]

        print(f"{content=}")
        start = time.time()

        if content.startswith("help"):
            await self.help(content, user)
        elif content.startswith("crawl_world"):
            await self.crawl_world(content, user)
        elif content.startswith("find_ally"):
            await self.find_ally(content, user)
        elif content == "ping":
            await user.send("pong")
        else:
            await user.send("Unknown command", mention_author=True)
        end = time.time()
        await user.send(f"elapsed: {end-start:.2f}s")

# intents = discord.Intents.default()
intents = discord.Intents.all()

client = BotMain(intents=intents)

client.run(discord_token)
