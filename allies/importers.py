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
            "Starting ally crawler for price: "
            "%d with page count: %d "
            "with start_page: %d",
            price, page_count, start_page
        )

        lowest_price = -1
        highest = {"total": 0, "price": 0}
        limit = 50
        sleep_time = 30
        not_found = 0
        for i in range(start_page, limit*page_count, limit):
            data = {'allies' : []}
            while True:
                # Loop if the exception occured (so we don't skip)
                try:
                    print(f"Page count: {i} out of {limit*page_count}")
                    data = self.api.get_allies_by_price(price=price, limit=limit, offset=i)
                except TokenException as exception:
                    logger.info(
                        "AllyByPriceImporter - Token exception found\n"
                        "Sleeping for %d seconds before retry.\n"
                        "Exception: %s", sleep_time, exception
                    )
                    time.sleep(sleep_time)
                break

            allies = self.format_allies(data["allies"])
            if len(allies) != limit:
                print(f"WARNING: Allies count: {len(allies)} smaller than {limit=}, {not_found=}")
                not_found += 1
            else:
                not_found = 0

            if not_found > 10:
                # Stop if 10 searches returned nothing
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
                    print(f"{highest['username']} with {total=}")

            if 'username' in highest:
                # Make sure the item is set
                print(
                    f"'{highest['username']}' with {highest['total']=} for {highest['price']=:,}"
                )
                print(f'{highest["g"]} / {highest["b"]} / {highest["s"]}')

            print(f"Lowest price: {lowest_price}")

            self.update_or_create_allies(allies)
            self.create_historical_allies(allies)

        if 'username' in highest:
            # Make sure the item is set
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
            data = self.api.get_allies_by_price(price, 25, 0)
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
