import logging
import time
import random
from typing import Dict, List

from api import HeckfireApi, TokenException
from .models import Ally, HistoricalAlly, Clan

# Get an instance of a logger
logger = logging.getLogger(__name__)


class BaseAllyImporter:
    def __init__(self, token: str, staytoken: str):
        self.api = HeckfireApi(token=token, staytoken=staytoken)
        self.model_fields = [f.name for f in Ally._meta.get_fields()]
        self.ally_requests_per_minute = 20
        self.created_count = 0
        self.updated_count = 0

    def format_allies(self, allies) -> List[Dict]:
        results = []
        for ally in allies:
            try:
                data = {
                    key: value
                    for key, value in ally.items()
                    if key in self.model_fields
                }
                data["owner"] = self.process_owner(data["owner"])

                # logger.info(f"Found ally: {data['username']}")
            except (TypeError, AttributeError) as e:
                pass
                # logger.info(f"NoneType Error Exception: {e}")
            results.append(data)
        return results

    def process_owner(self, owner_data: Dict) -> Ally:
        data = {
            key: value for key, value in owner_data.items() if key in self.model_fields
        }
        return self.update_or_create_ally(data)

    def update_or_create_allies(self, data: List[Dict]) -> None:
        for row in data:
            self.update_or_create_ally(row)

    def update_or_create_ally(self, data: Dict) -> Ally:
        ally_data = data.copy()
        user_id = ally_data.pop("user_id")
        obj, created = Ally.objects.update_or_create(
            user_id=user_id, defaults=ally_data
        )
        self.record_count(created)
        return obj

    def create_historical_allies(self, data: List[Dict]) -> None:
        for row in data:
            self.create_historical_ally(row)

    def create_historical_ally(self, data: Dict) -> HistoricalAlly:
        obj, created = HistoricalAlly.objects.get_or_create(**data)
        self.record_count(created)
        return obj

    def record_count(self, created):
        if created:
            self.created_count += 1
        else:
            self.updated_count += 1


class AllyByPriceImporter(BaseAllyImporter):
    def execute(self, price: int, page_count: int, start_page: int):
        logger.info(
            f"Starting ally crawler for price: "
            f"{price} with page count: {page_count} "
            f"with start_page: {start_page}"
        )

        highest = {"total": 0, "price": 0}
        for i in range(start_page, page_count):
            print(f"page_count: {i}")
            try:
                data = self.api.get_allies_by_price(price, i)
            except TokenException as e:
                logger.info(
                    f"AllyByPriceImporter - Token exception found, sleeping for 60 seconds before retry. Exception: {e}"
                )
                time.sleep(60)
            data = self.api.get_allies_by_price(price, i)
            allies = self.format_allies(data["allies"])
            for ally in allies:
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
                    print(f"{highest['username']} with {total=}")

            print(
                f"'{highest['username']}' with {highest['total']=} for {highest['price']=:,}"
            )
            print(f'{highest["g"]} / {highest["b"]} / {highest["s"]}')

            self.update_or_create_allies(allies)
            self.create_historical_allies(allies)

        print(f"'{highest['username']}' with {highest['total']=}")

        logger.info(f"Created {self.created_count} records")
        logger.info(f"Updated {self.updated_count} records")
        stay_alive = self.api.stay_alive()
        logger.info(f"Keeping token alive: {stay_alive['timestamp']}")
        self.api.collect_loot()
        logger.info(f"Collecting Loot")


class RandomAllyByPriceImporter(BaseAllyImporter):
    def execute(self):
        price = random.randint(0, 8000000000)
        try:
            logger.info(f"Starting ally crawler for price: {price}")
            data = self.api.get_allies_by_price(price, 1)
        except TokenException as e:
            logger.info(
                f"RandomAllyByPriceImporter - Token exception found, sleeping for 60 seconds before retry. Exception: {e}"
            )
            time.sleep(60)
        allies = self.format_allies(data["allies"])
        self.update_or_create_allies(allies)
        self.create_historical_allies(allies)
        logger.info(f"Created {self.created_count} records")
        logger.info(f"Updated {self.updated_count} records")
        stay_alive = self.api.stay_alive()
        logger.info(f"Keeping token alive: {stay_alive['timestamp']}")
        self.api.collect_loot()
        logger.info(f"Collecting Loot")


class AllyByNameImporter(BaseAllyImporter):
    def execute(self, seed_list: List, depth: int):
        for name in seed_list:
            logger.info(f"Crawling name: {name} with a depth of {depth}")
            stay_alive = self.api.stay_alive()
            logger.info(f"Keeping token alive: {stay_alive['timestamp']}")
            self.api.collect_loot()
            logger.info(f"Collecting Loot")
            self.crawl_name(name, depth)
        logger.info(f"Created {self.created_count} records")
        logger.info(f"Updated {self.updated_count} records")

    def crawl_name(self, name: str, depth: int):
        if not depth:
            return
        try:
            data = self.api.get_ally_by_name(name)
            time.sleep(3)
            stay_alive = self.api.stay_alive()
            logger.info(f"Keeping token alive: {stay_alive['timestamp']}")
        except TokenException as e:
            logger.info(
                f"AllyByNameImporter - Token exception found, sleeping for 60 seconds before retry. Exception: {e}"
            )
            time.sleep(60)
            data = self.api.get_ally_by_name(name)
        try:
            ally = self.format_allies(data["allies"])[0]
            self.update_or_create_ally(ally)
            self.create_historical_allies([ally])
            owner = ally["owner"]
            if owner and owner.username:
                self.crawl_name(owner.username, depth - 1)
        except IndexError as e:
            logger.info(f"Index Error (Ally changed name since scrape?) Exception: {e}")


class UpdateAllyImporter(BaseAllyImporter):
    def execute(self, name: str):
        logger.info(f"Updating name: {name}")
        stay_alive = self.api.stay_alive()
        logger.info(f"Keeping token alive: {stay_alive['timestamp']}")
        self.api.collect_loot()
        logger.info(f"Collecting Loot")
        try:
            data = self.api.get_ally_by_name(name)
        except TokenException as e:
            logger.info(
                f"UpdateAllyImporter - Token exception found, sleeping for 60 seconds before retry. Exception: {e}"
            )
            time.sleep(60)
            data = self.api.get_ally_by_name(name)
        try:
            ally = self.format_allies(data["allies"])[0]
            self.update_or_create_ally(ally)
            self.create_historical_allies([ally])
        except IndexError as e:
            logger.info(f"Index Error (Ally changed name since scrape?) Exception: {e}")
        logger.info(f"Created {self.created_count} records")
        logger.info(f"Updated {self.updated_count} records")


class ClanImporter:
    def __init__(self, token: str, staytoken: str):
        self.api = HeckfireApi(token=token, staytoken=staytoken)
        self.model_fields = [f.name for f in Clan._meta.get_fields()]
        self.created_count = 0
        self.updated_count = 0

    def format_clan(self, data) -> List[Dict]:
        results = []
        try:
            data = {
                key: value for key, value in Clan.items() if key in self.model_fields
            }
            logger.info(f"Found clan: {data['name']}")
        except (TypeError, AttributeError) as e:
            logger.info(f"NoneType Error Exception: {e}")
        results.append(data)
        return results

    def update_or_create_allies(self, data: List[Dict]) -> None:
        for row in data:
            self.update_or_create_ally(row)

    def update_or_create_ally(self, data: Dict) -> Clan:
        clan_data = data.copy()
        id = clan_data.pop("id")
        obj, created = Clan.objects.update_or_create(id=id, defaults=clan_data)
        self.record_count(created)
        return obj

    def record_count(self, created):
        if created:
            self.created_count += 1
        else:
            self.updated_count += 1

    def execute(self, group_id: int):
        logger.info(f"Starting clan crawler: {group_id}")
        try:
            data = self.api.get_clan_by_id(group_id)
        except TokenException as e:
            logger.info(
                f"ClanImporter - Token exception found, sleeping for 60 seconds before retry. Exception: {e}"
            )
            time.sleep(60)
        data = self.api.get_clan_by_id(group_id)
        clans = self.format_clan(data)
        self.update_or_create_allies(clans)

        logger.info(f"Created {self.created_count} records")
        logger.info(f"Updated {self.updated_count} records")
        stay_alive = self.api.stay_alive()
        logger.info(f"Keeping token alive: {stay_alive['timestamp']}")
        self.api.collect_loot()
        logger.info(f"Collecting Loot")
