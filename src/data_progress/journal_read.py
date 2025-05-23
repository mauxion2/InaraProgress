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
from inara_progress.progresslog import get_progress_log


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
        self.type_scan: int = 0
        self.curent_system: int = 0
        self.curent_system_name: str = ''
        self.pos_null: list[float] = [0.0, 0.0, 0.0]


this = This()
LOG = get_progress_log()
logger = get_plugin_logger(const.plugin_name)


class ParseJournal:
    """
    This class is a general purpose container to process individual journal files. It's used both by the main
    EDMC journal parser hook and by the threaded journal import function, generally called by other plugins.
    """
    def __init__(self):
        self.session: Session = db.get_session()

    def open_journal(self, journal_path: Path):
        
        file_journal = open(journal_path, 'r')
        while True:
            line = file_journal.readline()
            if line:
                try:
                    entry: Mapping[str, Any] = json.loads(line)
                    if this.type_scan == 4:
                        self.rescue_entry(entry) 
                    if this.type_scan == 3:
                        self.trade_entry(entry)
                    if this.type_scan == 2:
                        self.thargoids_entry(entry)
                    if this.type_scan == 0 or this.type_scan == 1:
                        self.line_entry(entry)
                except Exception as ex:
                    logger.error(f'Invalid journal entry:\n{line!r}\n', exc_info=ex)
            else:
                break

    def load_journal(self, journal_path: Path) -> int:

        # if event.is_set():
        #    return True
        if self.session.query(func.count(db.JournalLog.journal)).scalar() < 1:
            db.set_setting('InaraProgress_exploration_Jumps', 0)
            db.set_setting('InaraProgress_exploration_L3scan', 0)
            db.set_setting("InaraProgress_exobiologist_Organic", 0)
            db.set_setting('InaraProgress_Rescue_Pods', 0)
            db.set_setting('InaraProgress_Rescue_Passenger', 0)

        if this.type_scan == 0 or this.type_scan == 1:
            found = self.session.scalar(select(db.JournalLog).where(db.JournalLog.journal == journal_path.name))
        else:
            found = None

        if not found:
            self.open_journal(journal_path)
        else:
            self.session.expunge(found)
            return 2
        
        if this.type_scan == 0 or this.type_scan == 1:
            journal = db.JournalLog(journal=journal_path.name)
            try:
                self.session.add(journal)
                self.session.commit()
            except (IntegrityError, AlcIntegrityError):
                self.session.expunge(journal)

        return 0

    def time_entry(self, entry: Mapping[str, Any]) -> str:
        timestamp = entry["timestamp"]   # "timestamp":"2024-05-28T08:00:00Z"
        timestamp = timestamp.replace("T", " ")
        timestamp = timestamp.replace("Z", "")
        return timestamp 

    def thargoids_entry(self, entry: Mapping[str, Any]) -> None:
        timestamp = self.time_entry(entry)
        time_event = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        event_type = entry['event'].lower()
        if event_type == 'factionkillbond':
            self.targ_entry(entry, timestamp, time_event)

    def targ_entry(self, entry: Mapping[str, Any], timestamp: str, time_event: datetime):
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

                    if reward == UP1402_SCOUT1_TARG or reward == UP1402_SCOUT2_TARG or reward == _SCOUT_TARG:
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

                if db.thargoid_add(timestamp, targ_name, reward):
                    thargoid_kill = db.get_thargoid_count()
                    thargoid_type_count = db.get_thargoid_type_count(targ_name)
                    self.saved_thargoid_type_count(thargoid_type_count, targ_name)
                    db.set_setting('InaraProgress_thargoid_kill', thargoid_kill)  

    def trade_entry(self, entry: Mapping[str, Any]) -> None:
        timestamp = self.time_entry(entry)
        event_type = entry['event'].lower()
        match event_type:
            case 'docked':
                if entry["StationType"] == "FleetCarrier":
                    db.set_docked_fleet(entry["MarketID"])

            case 'marketsell':                
                if 'MarketID' in entry:
                    market = entry["MarketID"]
                    if db.get_docked_fleet(market):
                        pr_cr = entry["Count"] * (entry["SellPrice"] - entry["AvgPricePaid"])
                        if pr_cr > 0: 
                            db.set_trade(timestamp, market, pr_cr)

            case 'searchandrescue':
                if 'MarketID' in entry:
                    market = entry["MarketID"]
                    db.set_trade(timestamp, market, entry["Reward"])

            case 'missioncompleted':
                name_mission = entry["Name"]
                if name_mission == 'Mission_PassengerBulk_name' or name_mission == 'Mission_TW_RefugeeBulk':
                    db.set_trade(timestamp, 0, entry["Reward"])


    def rescue_entry(self, entry: Mapping[str, Any]) -> None:
        event_type = entry['event'].lower()
        match event_type:
            case 'missionaccepted':
                if "PassengerCount" in entry:
                    name_mission = entry["Name"]     
                    if name_mission == 'Mission_TW_RefugeeBulk':
                        db.set_mission(entry["MissionID"], entry["PassengerCount"], entry["PassengerVIPs"], entry["Reward"])

            case 'missioncompleted':
                if "Commodity" in entry:
                    cargo_type = entry["Commodity"]
                    if cargo_type == '$OccupiedCryoPod_Name;':
                        # pr_cr = entry["Reward"]
                        rescue_pods = db.get_setting('InaraProgress_Rescue_Pods') 
                        rescue_pods += entry["Count"]
                        db.set_setting('InaraProgress_Rescue_Pods', rescue_pods)
                else:
                    mission_id = entry["MissionID"]
                    if db.find_id_mission(mission_id):
                        passenger_count = db.get_passenger_count(mission_id)
                        if entry["Name"] == 'Mission_TW_RefugeeBulk_name':
                            rescue_passenger = db.get_setting('InaraProgress_Rescue_Passenger') 
                            rescue_passenger += passenger_count
                            db.set_setting('InaraProgress_Rescue_Passenger', rescue_passenger)
                            db.finish_mission(mission_id)


    def line_entry(self, entry: Mapping[str, Any]) -> None:
        """
        Main journal entry processor. Parses important events and submits the appropriate data objects to the database.

        :param entry: JSON object of the current journal line
        """
        timestamp = self.time_entry(entry)
        time_event = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        event_type = entry['event'].lower()
        match event_type:

            case 'fssdiscoveryscan':
                if "SystemAddress" in entry:
                    this.curent_system = entry["SystemAddress"]
                    this.curent_system_name = entry["SystemName"]
                db.check_system(this.curent_system, this.curent_system_name, this.pos_null, False)
                db.set_system_bc(this.curent_system, entry["BodyCount"])

            case 'supercruiseentry':
                this.curent_system = entry["SystemAddress"]
                this.curent_system_name = entry["StarSystem"]
                db.check_system(this.curent_system, entry["StarSystem"], this.pos_null, False)

            case 'fsdjump':
                this.curent_system = entry["SystemAddress"]
                this.curent_system_name = entry["StarSystem"]
                exploration_jumps = db.get_setting('InaraProgress_exploration_Jumps')
                exploration_jumps += 1
                db.set_setting('InaraProgress_exploration_Jumps', exploration_jumps)
                if not db.check_system(this.curent_system, this.curent_system_name, entry["StarPos"], True):
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
                    exobiologist_unique = db.get_bio_unique_count()
                    db.set_setting("InaraProgress_exobiologist_Unique", exobiologist_unique)
                    db.set_bio(timestamp, system_id, db.name_system(system_id),
                               planet_id, db.name_planet(system_id, planet_id), bio_name, bio_variant, bio_codex)
                    db.set_sell_bio(timestamp, system_id, planet_id, bio_codex, bio_name, bio_variant, bio_cost)

            case 'sellorganicdata':                    
                bio_data_tab = entry["BioData"]
                bio_data_tab_len = len(bio_data_tab)
                sell_bio_count = db.get_sell_bio_count()
                if bio_data_tab_len > sell_bio_count:
                    text_error = 'ERROR table DB len: {}'.format(sell_bio_count)
                else:
                    text_error = ''    
                db.set_sell_date_died(timestamp, bio_data_tab_len, text_error, '', '')
                
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
                        db.delete_sell_bio(bio_codex, bio_name, bio_variant)
                elif bio_data_tab_len > sell_bio_count:
                    text_error = 'T {} Count Bio {} Count DB {}\n '.format(timestamp, bio_data_tab_len, sell_bio_count)
                    text_error += 'ERROR bio data sell table larger than table DB'
                    LOG.log(text_error, "INFO")

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
                self.targ_entry(entry, timestamp, time_event)

            case 'docked':
                this.curent_system = entry["SystemAddress"]
                this.curent_system_name = entry["StarSystem"]
                db.check_system(this.curent_system, this.curent_system_name, this.pos_null, False)
                if entry["StationType"] == "FleetCarrier":
                    db.set_docked_fleet(entry["MarketID"])

            case 'fssallbodiesfound':
                this.curent_system = entry["SystemAddress"]
                this.curent_system_name = entry["SystemName"]
                db.check_system(this.curent_system, this.curent_system_name, this.pos_null, False)
                db.set_system_bc(this.curent_system, entry["Count"])

            case 'location':
                this.curent_system = entry["SystemAddress"]
                this.curent_system_name = entry["StarSystem"]
                db.check_system(this.curent_system, this.curent_system_name, entry["StarPos"], True)

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
                            # trade_profit = db.get_trade_profit()
                            # db.set_setting("InaraProgress_trade_profit", trade_profit)

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
                    # trade_profit = db.get_trade_profit()
                    # db.set_setting("InaraProgress_trade_profit", trade_profit)

            case 'missionaccepted':
                self.rescue_entry(entry)
							
            case 'missioncompleted':
                self.rescue_entry(entry)                

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
                db.set_setting('InaraProgress_thargoid_orthrus', thargoid_type_count)
            case 'Banshees':
                pass
            case 'Revenant':
                pass


def get_filepaths(directory):

    # Function to create a list of tuples
    def create_list_of_tuples(lst1, lst2):
        result = []  # Empty list to store the tuples
        for i in range(len(lst1)):
            # Create a tuple from corresponding elements
            tuple_element = (lst1[i], lst2[i])
            result.append(tuple_element)  # Append the tuple to the list
        return result

    file_paths: list[Path] = []
    timestamp: list[datetime] = []

    for journal_file in os.listdir(directory):
        if journal_file.endswith(".log"):
            path_journal_file = Path(directory) / journal_file
            file_paths.append(path_journal_file)
            # Journal.2022-03-23T20 47 19.01.log
            # Journal.  18 04 21 19 18 18.01.log
            journal_file = journal_file.replace("Journal.", "")
            journal_file = journal_file.replace(".01.log", "")
            journal_file = journal_file.replace("T", "")
            journal_file = journal_file.replace("-", "")
            if len(journal_file) == 12:
                journal_file = '20' + journal_file 
            timestamp.append(datetime.datetime.strptime(journal_file, '%Y%m%d%H%M%S'))

    list_of_tuples = create_list_of_tuples(timestamp, file_paths)
    list_of_tuples.sort()
    journal_files: list[Path] = [journal[1] for journal in list_of_tuples]

    return journal_files


def parse_journal(journal_path: Path) -> int:
    
    if this.type_scan == 2 or this.type_scan == 3 or this.type_scan == 4:
        ParseJournal().open_journal(journal_path)
        return 0 
    return ParseJournal().load_journal(journal_path)


def clear_db(session: Session):

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

    db.clear_bio_unique()

    """"

    session.query(BioListCost).update({BioListCost.bio_find: None}) 
    session.commit()    
    exobiologist_Unique
    BioListCost
    .values(bio_find=1)
    session1.query(db.JournalLog).delete()
    session.query(BioListCost).filter(filter_conditions).update({bio_find: sa.text('')}, synchronize_session=False)
    session1.commit()
    """


def parse_journals(cl_db: int) -> None:
    this.type_scan = cl_db

    if not this.journal_run:
        session1: Session = db.get_session()
        match this.type_scan:
            case 1:
                # LOG.log('clear_db : '+str(this.type_scan), "INFO")
                clear_db(session1)
            case 2:
                # LOG.log('db.ThargoidList delete : '+str(this.type_scan), "INFO")
                session1.query(db.ThargoidList).delete()
                session1.commit()
            case 3:
                # LOG.log('db.TradeList delete : '+str(this.type_scan), "INFO")
                session1.query(db.TradeList).delete()
                session1.commit()
            case 4:
                db.set_setting('InaraProgress_Rescue_Pods', 0)
                db.set_setting('InaraProgress_Rescue_Passenger', 0)

        this.journal_run = True
        journal_works(session1)
        # LOG.log('type_scan '+str(this.type_scan), "INFO")


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
            pass
            parse_journal(f)

        db.clear_lost_bio()
        db.export_bio_lost_sumary()

    except Exception as ex:
        logger.error('Journal parsing failed', exc_info=ex)

    this.journal_run = False
