# -*- coding: utf-8 -*-
# Licensed under the [GNU Public License (GPL)](http://www.gnu.org/licenses/gpl-2.0.html) version 2 or later.


import json
import os
import datetime
from os.path import expanduser
from pathlib import Path
# import concurrent.futures
from typing import Any, Mapping

from sqlalchemy import select, func  # , Table, MetaData
from sqlalchemy.exc import IntegrityError as AlcIntegrityError
from sqlalchemy.orm import Session
from sqlite3 import IntegrityError

from EDMCLogging import get_plugin_logger
from config import config

from data_progress import const
from data_progress import data_db as db


_HYDRA_TARG = 60000000
_ORTHRUS_TARG = 30000000
_MEDUSA_TARG = 40000000
_BASILISK_TARG = 24000000
_CYCLOPS_TARG = 8000000
_SCOUT_TARG = 80000

UP1402_HYDRA_TARG = 50000000
UP1402_ORTHRUS_TARG = 40000000
UP1402_MEDUSA_TARG = 34000000
UP1402_BASILISK_TARG = 20000000
UP1402_CYCLOPS_TARG = 6500000

UP1402_HUNTER_TARG = 4500000
UP1402_SCOUT2_TARG = 75000
UP1402_SCOUT1_TARG = 65000

BANSHEES_TARG = 1000000 
REVENANT_TARG = 25000 

UP1806_HYDRA_TARG = 60000000
UP1806_ORTHRUS_TARG = 15000000
UP1806_MEDUSA_TARG = 40000000
UP1806_BASILISK_TARG = 24000000
UP1806_CYCLOPS_TARG = 8000000


""" 

31-01-2023  15-17godz
Thargoid Type   Pre-Update 14.02    Post Update 14.02
Scout (Marauder)        80k                   65k
Scout (Other variants)  80k                   75k
Cyclops                  8mil                 6.5mil
Basilisk                24mil                 20mil
Hydra                   60mil                 50mil
Medusa                  40mil                 34mil
Orthrus                 30mil                 25mil 40mil ?

Scavenger  Revenant
    28-05-2024
    Update 18.06
    Cyclops   6,500,000 →  8,000,000
    Basilisk 20,000,000 → 24,000,000
    Medusa   34,000,000 → 40,000,000
    Hydra    50,000,000 → 60,000,000
    Orthrus  40,000,000 → 15,000,000
"""


class This:

    def __init__(self):

        dir_path = config.get_str('journaldir')
        dir_path = dir_path if dir_path else config.default_journal_dir_path
        self.journal_dir_path = expanduser(dir_path)
        self.journal_run: bool = False
        self.curent_system: int = 0


this = This()
logger = get_plugin_logger(const.plugin_name)


class ParseJournal:
    """
    This class is a general purpose container to process individual journal files. It's used both by the main
    EDMC journal parser hook and by the threaded journal import function, generally called by other plugins.
    """
    def __init__(self):
        self.session: Session = db.get_session()

    def load_journal(self, journal_path: Path) -> int:

        # if event.is_set():
        #    return True
        if self.session.query(func.count(db.JournalLog.journal)).scalar() < 1:
            db.set_setting('InaraProgress_exploration_Jumps', 0)
            db.set_setting('InaraProgress_exploration_L3scan', 0)
            db.set_setting("InaraProgress_exobiologist_Organic", 0)

        found = self.session.scalar(select(db.JournalLog).where(db.JournalLog.journal == journal_path.name))

        if not found:

            file_journal = open(journal_path, 'r')
            while True:
                line = file_journal.readline()
                if line:
                    try:
                        entry: Mapping[str, Any] = json.loads(line)
                        self.line_entry(entry)
                    except Exception as ex:
                        logger.error(f'Invalid journal entry:\n{line!r}\n', exc_info=ex)
                else:
                    break

        else:
            self.session.expunge(found)
            return 2
        
        journal = db.JournalLog(journal=journal_path.name)
        try:
            self.session.add(journal)
            self.session.commit()
        except (IntegrityError, AlcIntegrityError):
            self.session.expunge(journal)

        return 0

    def line_entry(self, entry: Mapping[str, Any]) -> None:
        """
        Main journal entry processor. Parses important events and submits the appropriate data objects to the database.

        :param entry: JSON object of the current journal line
        """
        timestamp = entry["timestamp"]   # "timestamp":"2024-05-28T08:00:00Z"
        timestamp = timestamp.replace("T", " ")
        timestamp = timestamp.replace("Z", "")
        time_event = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        event_type = entry['event'].lower()
        match event_type:

            case 'fsdjump':
                this.curent_system = entry["SystemAddress"]
                exploration_jumps = db.get_setting('InaraProgress_exploration_Jumps')
                exploration_jumps += 1
                db.set_setting('InaraProgress_exploration_Jumps', exploration_jumps)
                if not db.check_system(entry["SystemAddress"], entry["StarSystem"]):
                    exploration_visited = db.get_system_list_count()
                    db.set_setting('InaraProgress_exploration_Visited', exploration_visited)

            case 'fssbodysignals':                   # saasignalsfound   fssbodysignals
                exploration_l3scan = db.get_setting('InaraProgress_exploration_L3scan')
                exploration_l3scan += 1
                db.set_setting('InaraProgress_exploration_L3scan', exploration_l3scan)
                if "Signals" in entry:
                    sig = entry["Signals"]
                    for sg in sig:
                        if "Type_Localised" in sg:
                            localised = sg['Type_Localised']
                            if localised == "Biological":
                                db.check_planet_biofss(entry["BodyID"], entry["BodyName"],
                                                       entry["SystemAddress"], sg["Count"])

            case 'saasignalsfound':                   # saasignalsfound   fssbodysignals
                if "Signals" in entry:
                    sig = entry["Signals"]
                    for sg in sig:
                        if "Type_Localised" in sg:
                            localised = sg['Type_Localised']
                            if localised == "Biological":
                                if not db.check_planet_biosaa(entry["BodyID"], entry["BodyName"],
                                                              entry["SystemAddress"], sg["Count"]):
                                    exobiologist_planets = db.get_planet_biosaa_count()
                                    db.set_setting("InaraProgress_exobiologist_Planets", exobiologist_planets)

            case 'scanorganic':
                if entry["ScanType"] == "Analyse":
                    system_id = entry["SystemAddress"]
                    planet_id = entry["Body"]
                    bio_codex = entry["Species"]
                    bio_name = entry["Species_Localised"]
                    db.set_sell_date_died(timestamp, 0, db.name_system(system_id), 
                                          db.name_planet(system_id, planet_id), bio_name)
                    if "Variant_Localised" in entry:
                        bio_variant = entry["Variant_Localised"]
                        bio_variant = bio_variant.replace(bio_name, "")
                        bio_variant = bio_variant.replace(" - ", "")
                    else:
                        bio_variant = 'unknown'    
                    bio_cost = db.get_bio_cost(bio_codex)
                    db.set_bio(timestamp, system_id, db.name_system(system_id),
                               planet_id, db.name_planet(system_id, planet_id), bio_name, bio_variant, bio_codex)
                    db.set_sell_bio(timestamp, system_id, planet_id, bio_codex, bio_name, bio_variant, bio_cost)

            case 'sellorganicdata':                    
                bio_data_tab = entry["BioData"]
                bio_data_tab_len = len(bio_data_tab)
                db.set_sell_date_died(timestamp, bio_data_tab_len, '', '', '')
                sell_bio_count = db.get_sell_bio_count()
                exobiologist_organic = db.get_setting('InaraProgress_exobiologist_Organic')
                exobiologist_organic += bio_data_tab_len
                db.set_setting("InaraProgress_exobiologist_Organic", exobiologist_organic)                
                
                if bio_data_tab_len == sell_bio_count:
                    db.finish_sell_bio()
                elif (bio_data_tab_len > 0) and (bio_data_tab_len < sell_bio_count):
                    for bio in bio_data_tab:
                        bio_codex = bio["Species"]
                        bio_name = bio["Species_Localised"]
                        if "Variant_Localised" in bio:
                            bio_variant = bio["Variant_Localised"]
                            bio_variant = bio_variant.replace(bio_name, "")
                            bio_variant = bio_variant.replace(" - ", "")
                        else:
                            bio_variant = 'unknown'    
                        bio_cost = bio["Value"]
                        db.delete_sell_bio(bio_codex, bio_name, bio_variant, bio_cost)

            case 'died':
                if 'KillerName' in entry:
                    tx = entry["KillerName"]
                else:
                    tx = 'died'
                db.set_sell_date_died(timestamp, 0, tx, '', '')
                if db.get_sell_bio_count() > 0:
                    db.export_bio_lost(time_event)
                    db.finish_sell_bio()    

            case 'factionkillbond':
                if 'VictimFaction_Localised' in entry:
                    targ = entry["VictimFaction_Localised"]
                    if targ == 'Thargoids':
                        reward = entry["Reward"]

                        time_patch_18_06 = datetime.datetime(2024, 5, 28, 8, 0, 0)
                        time_patch_14_02 = datetime.datetime(2023, 1, 31, 15, 0, 0)
                        targ_name = 'none name'

                        if time_patch_14_02 > time_event:

                            if reward == _SCOUT_TARG:
                                targ_name = 'Scout'

                            if reward == _CYCLOPS_TARG:
                                targ_name = 'Cyclops'

                            if reward == _BASILISK_TARG:
                                targ_name = 'Basilisk'

                            if reward == _MEDUSA_TARG:
                                targ_name = 'Medusa'

                            if reward == _HYDRA_TARG:
                                targ_name = 'Hydra'

                            if reward == _ORTHRUS_TARG:
                                targ_name = 'Orthrus'

                        if time_patch_14_02 < time_event: 

                            if reward == UP1402_SCOUT1_TARG or reward == UP1402_SCOUT2_TARG:
                                targ_name = 'Scout'

                            if reward == UP1402_HUNTER_TARG:
                                targ_name = 'Hunter'
                        
                        if time_patch_14_02 < time_event < time_patch_18_06:

                            if reward == UP1402_CYCLOPS_TARG:
                                targ_name = 'Cyclops'

                            if reward == UP1402_BASILISK_TARG:
                                targ_name = 'Basilisk'

                            if reward == UP1402_MEDUSA_TARG:
                                targ_name = 'Medusa'

                            if reward == UP1402_HYDRA_TARG:
                                targ_name = 'Hydra'

                            if reward == UP1402_ORTHRUS_TARG:
                                targ_name = 'Orthrus'

                        if time_event > time_patch_18_06:

                            if reward == UP1806_CYCLOPS_TARG:
                                targ_name = 'Cyclops'

                            if reward == UP1806_BASILISK_TARG:
                                targ_name = 'Basilisk'

                            if reward == UP1806_MEDUSA_TARG:
                                targ_name = 'Medusa'

                            if reward == UP1806_HYDRA_TARG:
                                targ_name = 'Hydra'

                            if reward == UP1806_ORTHRUS_TARG:
                                targ_name = 'Orthrus'                              

                        if reward == BANSHEES_TARG:
                            targ_name = 'Banshees'

                        if reward == REVENANT_TARG:
                            targ_name = 'Revenant'

                        db.thargoid_add(timestamp, targ_name, reward)
                        thargoid_kill = db.get_thargoid_count()
                        thargoid_type_count = db.get_thargoid_type_count(targ_name)
                        self.saved_thargoid_type_count(thargoid_type_count, targ_name)
                        db.set_setting('InaraProgress_thargoid_kill', thargoid_kill)                        

            case 'docked':
                if entry["StationType"] == "FleetCarrier":
                    db.set_docked_fleet(entry["MarketID"])

            case 'marketsell':                
                if 'MarketID' in entry:
                    market = entry["MarketID"]
                    if db.get_docked_fleet(market):
                        db.set_market(this.curent_system, market, 'sell')   # "StolenGoods":true, "BlackMarket":true
                        trading_markets = db.get_market_count()
                        db.set_setting('InaraProgress_trading_Markets', trading_markets)
                        pr_cr = entry["Count"] * (entry["SellPrice"] - entry["AvgPricePaid"])
                        if pr_cr > 0: 
                            db.set_trade(timestamp, market, pr_cr)
                            trade_profit = db.get_trade_profit()
                            db.set_setting("InaraProgress_trade_profit", trade_profit)

            case 'marketbuy': 
                if 'MarketID' in entry:
                    market = entry["MarketID"]                
                    if db.get_docked_fleet(market):   
                        db.set_market(this.curent_system, market, 'buy')
                        trading_markets = db.get_market_count()
                        db.set_setting('InaraProgress_trading_Markets', trading_markets)

            case 'searchandrescue':
                if 'MarketID' in entry:
                    market = entry["MarketID"]
                    db.set_market(this.curent_system, market, 'rescue')
                    trading_markets = db.get_market_count()
                    db.set_setting('InaraProgress_trading_Markets', trading_markets)
                    db.set_trade(timestamp, market, entry["Reward"])
                    trade_profit = db.get_trade_profit()
                    db.set_setting("InaraProgress_trade_profit", trade_profit)

    @staticmethod
    def saved_thargoid_type_count(thargoid_type_count: int, targ_name: str):
        match targ_name:
            case 'Scout':
                db.set_setting('InaraProgress_thargoid_scout', thargoid_type_count)
            case 'Cyclops':
                db.set_setting('InaraProgress_thargoid_cyclops', thargoid_type_count)
            case 'Hunter':
                db.set_setting('InaraProgress_thargoid_hunter', thargoid_type_count)
            case 'Basilisk':
                db.set_setting('InaraProgress_thargoid_basilisk', thargoid_type_count)
            case 'Medusa':
                db.set_setting('InaraProgress_thargoid_medusa', thargoid_type_count)
            case 'Hydra':
                db.set_setting('InaraProgress_thargoid_hydra', thargoid_type_count)
            case 'Orthrus':
                pass
            case 'Banshees':
                pass
            case 'Revenant':
                pass


def get_filepaths(directory):

    file_paths: list[Path] = []

    for journal_file in os.listdir(directory):
        if journal_file.endswith(".log"):
            journal_file = Path(directory) / journal_file
            file_paths.append(journal_file)

    return file_paths


def parse_journal(journal_path: Path) -> int:

    return ParseJournal().load_journal(journal_path)


def clear_db(session1: Session):

    db.drop_table('journal_log')
    db.drop_table('mission')
    db.drop_table('planet_bio_fss')
    db.drop_table('planet_bio_saa')
    db.drop_table('bio_list')
    db.drop_table('bio_list2')
    db.drop_table('bio_lost')
    db.drop_table('bio_shell')
    db.drop_table('system_list')
    db.drop_table('thargoid_list')
    db.drop_table('market_list')
    db.drop_table('docked_fleet')
    db.drop_table('trade_list')
    db.drop_table('sell_date_died')
    db.db_create()

    """"
    session1.query(db.JournalLog).delete()
    session1.commit()
    """


def parse_journals(cl_db: bool) -> None:

    if not this.journal_run:
        session1: Session = db.get_session()
        if cl_db:
            clear_db(session1)
        this.journal_run = True
        journal_works(session1)


def journal_works(session1: Session) -> None:

    if this.journal_dir_path == '':
        this.journal_run = False
        return

    full_file_paths = get_filepaths(this.journal_dir_path)
    
    try:
        """ 
        count = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for f in full_file_paths:
                futures.append(executor.submit(parse_journal, f))
            for future in concurrent.futures.as_completed(futures):
                count += 1


        """
        for f in full_file_paths:
            parse_journal(f)

        db.clear_lost_bio()
        db.export_bio_lost_sumary()

    except Exception as ex:
        logger.error('Journal parsing failed', exc_info=ex)

    this.journal_run = False
