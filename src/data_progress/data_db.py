

import datetime
import os
# from typing import List
from typing import Optional
from sqlalchemy import Engine, create_engine, Executable, Result, MetaData  # , ForeignKey
from sqlalchemy import text, select, update, delete, String, func
from sqlalchemy.dialects.sqlite import insert

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
# from sqlalchemy.orm import relationship

from data_progress.const import database_version, plugin_name
from EDMCLogging import get_plugin_logger
from config import config

logger = get_plugin_logger(plugin_name)


class This:
    """Holds globals."""

    def __init__(self):
        self.sql_engine: Optional[Engine] = None
        self.sql_session_factory: Optional[scoped_session] = None


this = This()


"""
Define the SQLAlchemy Schemas
"""


class Base(DeclarativeBase):
    pass


class Metadata(Base):
    __tablename__ = 'metadata'

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(default='')


class JournalLog(Base):
    __tablename__ = 'journal_log'

    journal: Mapped[str] = mapped_column(String(32), primary_key=True)
    

class Settings(Base):
    __tablename__ = 'settings'

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(default='0')


class Mission(Base):
    __tablename__ = 'mission'

    MissionID: Mapped[int] = mapped_column(primary_key=True, default='0')
    PassengerCount: Mapped[int] = mapped_column(default='0')
    PassengerVIPs: Mapped[bool] = mapped_column(default=False)
    Reward: Mapped[int] = mapped_column(default='0')


class PlanetBioFSS(Base):
    __tablename__ = 'planet_bio_fss'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(default='0')
    planet_name: Mapped[str] = mapped_column(default='')
    system_id: Mapped[int] = mapped_column(default='0')
    bio_count: Mapped[int] = mapped_column(default='0')


class PlanetBioSAA(Base):
    __tablename__ = 'planet_bio_saa'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(default='0')
    planet_name: Mapped[str] = mapped_column(default='')
    system_id: Mapped[int] = mapped_column(default='0')
    bio_count: Mapped[int] = mapped_column(default='0')


class BioList(Base):
    __tablename__ = 'bio_list'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    system_id: Mapped[int] = mapped_column(default='0')
    planet_id: Mapped[int] = mapped_column(default='0')
    bio_codex: Mapped[str] = mapped_column(default='')
    bio_name: Mapped[str] = mapped_column(default='')


class BioListCost(Base):
    __tablename__ = 'bio_list_cost'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bio_codex: Mapped[str] = mapped_column(default='')
    bio_name: Mapped[str] = mapped_column(default='')
    bio_cost: Mapped[int] = mapped_column(default='0')
    bio_find: Mapped[int] = mapped_column(default='0')


class SystemList(Base):
    __tablename__ = 'system_list'

    system_id: Mapped[int] = mapped_column(primary_key=True)
    system_name: Mapped[str] = mapped_column(default='')


class ThargoidList(Base):
    __tablename__ = 'thargoid_list'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    thargoid_reward: Mapped[int] = mapped_column(default='0')
    thargoid_name: Mapped[str] = mapped_column(default='')
    thargoid_time: Mapped[str] = mapped_column(default='')


class MarketList(Base):
    __tablename__ = 'market_list'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    market_id: Mapped[int] = mapped_column(default='0')
    trade: Mapped[str] = mapped_column(default='')


class DockedFleet(Base):
    __tablename__ = 'docked_fleet'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    market_id: Mapped[int] = mapped_column(default='0')


class BioShell(Base):
    __tablename__ = 'bio_shell'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    system_id: Mapped[int] = mapped_column(default='0')
    planet_id: Mapped[int] = mapped_column(default='0')
    bio_codex: Mapped[str] = mapped_column(default='')
    bio_name: Mapped[str] = mapped_column(default='')
    bio_cost: Mapped[int] = mapped_column(default='0')
    bio_time: Mapped[str] = mapped_column(default='')


def run_statement(engine: Engine, statement: Executable) -> Result:
    """
    Execute a SQLAlchemy statement. Creates a fresh connection, commits, and closes the connection.

    :param engine: The SQLAlchemy engine
    :param statement: The SQLAlchemy statement to be executed
    """

    connection = engine.connect()
    result = connection.execute(statement)
    connection.commit()
    connection.close()
    return result


def init() -> None:
    """
    Initialize the database 
    """
    if not this.sql_engine:

        engine_path = config.app_dir_path / 'dataprogress.db'

        # Set up engine and construct DB

        this.sql_engine = create_engine(f'sqlite:///{engine_path}', connect_args={'timeout': 30})
        Base.metadata.create_all(this.sql_engine)
        run_statement(this.sql_engine, insert(Metadata).values(key='version', value=database_version)
                      .on_conflict_do_update(index_elements=['key'], set_=dict(value=database_version)))
        this.sql_session_factory = scoped_session(sessionmaker(bind=this.sql_engine))
    return


def shutdown() -> None:
    """
    Close open sessions and dispose of the SQL engine
    """

    try:
        connect = this.sql_engine.connect()
        connect.execute(text('VACUUM'))  # Optimize size of db file
        connect.commit()
        connect.close()
        this.sql_session_factory.close()
        this.sql_engine.dispose()
    except Exception as ex:
        logger.error('Error during cleanup commit', exc_info=ex)


def get_session() -> Session:
    """
    Get a thread-safe Session for the active DB Engine

    :return: Return a new thread-safe Session object
    """

    return this.sql_session_factory()


def get_engine() -> Engine:
    """
    Get the active SQLAlchemy Engine

    :return: Return the Engine object
    """

    return this.sql_engine


def truncate_db():
    # delete all table data (but keep tables)
    # we do cleanup before test 'cause if previous test errored,
    # DB can contain dust
    meta = MetaData(this.sql_engine, True)
    connect = this.sql_engine.connect()
    trans = connect.begin()
    for table in meta.sorted_tables:
        connect.execute(text(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;'))
        connect.execute(table.delete())
        connect.execute(text(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;'))
    trans.commit()


def truncate_db1():
    # delete all table data (but keep tables)
    # we do cleanup before test 'cause if previous test errored,
    # DB can contain dust
    meta = MetaData(this.sql_engine, True)
    con = this.sql_engine.connect()
    trans = con.begin()
    con.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))
    for table in meta.sorted_tables:
        con.execute(table.delete())
    con.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))
    trans.commit()


def truncate():
    target_metadata = Base.metadata
    this.sql_session_factory.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))
    for table in target_metadata.sorted_tables:
        this.sql_session_factory.execute(table.delete())
    this.sql_session_factory.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))
    this.sql_session_factory.commit()


def set_setting(key: str, value: int):
    data: Settings = this.sql_session_factory.scalar(select(Settings).where(Settings.key == key))
    if not data:
        data = Settings(key=key, value=value)
        this.sql_session_factory.add(data)
    else:
        stmt = update(Settings).where(Settings.key == key).values(value=value)
        this.sql_session_factory.execute(stmt)
    this.sql_session_factory.commit() 


def set_setting(key: str, value: float):
    data: Settings = this.sql_session_factory.scalar(select(Settings).where(Settings.key == key))
    if not data:
        data = Settings(key=key, value=value)
        this.sql_session_factory.add(data)
    else:
        stmt = update(Settings).where(Settings.key == key).values(value=value)
        this.sql_session_factory.execute(stmt)
    this.sql_session_factory.commit()


def get_setting(key: str) -> int:
    data: Settings = this.sql_session_factory.scalar(select(Settings).where(Settings.key == key))
    if not data:
        data = Settings(key=key, value='0')
        this.sql_session_factory.add(data)
        this.sql_session_factory.commit()
    return data.value


def set_mission(mission_id: int, passenger_count: int, passenger_vips: bool, reward: int):
    data = Mission(MissionID=mission_id, PassengerCount=passenger_count, PassengerVIPs=passenger_vips, Reward=reward)
    this.sql_session_factory.add(data)
    this.sql_session_factory.commit()


def find_id_mission(mission_id: int) -> bool:
    find_ok = True
    data: Mission = this.sql_session_factory.scalar(select(Mission).where(Mission.MissionID == mission_id))
    if not data:
        find_ok = False
    return find_ok


def get_passenger_count(mission_id: int) -> int:
    data: Mission = this.sql_session_factory.scalar(select(Mission).where(Mission.MissionID == mission_id))
    return data.PassengerCount


def get_vip(mission_id: int) -> bool:
    data: Mission = this.sql_session_factory.scalar(select(Mission).where(Mission.MissionID == mission_id))
    return data.PassengerVIPs 


def finish_mission(mission_id: int):
    stmt = delete(Mission).where(Mission.MissionID == mission_id)
    this.sql_session_factory.execute(stmt)
    this.sql_session_factory.commit()


def check_planet_biofss(body_id: int, body_name: str, system_id: int, bio_count: int) -> bool:
    check_planet = True
    data: PlanetBioFSS = this.sql_session_factory.scalar(select(PlanetBioFSS).where(PlanetBioFSS.planet_id == body_id)
                                                         .where(PlanetBioFSS.planet_name == body_name)
                                                         .where(PlanetBioFSS.system_id == system_id)
                                                         )
    if not data:
        data = PlanetBioFSS(planet_id=body_id, planet_name=body_name, system_id=system_id, bio_count=bio_count)
        this.sql_session_factory.add(data)
        this.sql_session_factory.commit()
        check_planet = False
    return check_planet


def check_planet_biosaa(body_id: int, body_name: str, system_id: int, bio_count: int) -> bool:
    check_planet = True
    data: PlanetBioSAA = this.sql_session_factory.scalar(select(PlanetBioSAA).where(PlanetBioSAA.planet_id == body_id)
                                                         .where(PlanetBioSAA.planet_name == body_name)
                                                         .where(PlanetBioSAA.system_id == system_id)
                                                         )
    if not data:
        data = PlanetBioSAA(planet_id=body_id, planet_name=body_name, system_id=system_id, bio_count=bio_count)
        this.sql_session_factory.add(data)
        this.sql_session_factory.commit()
        check_planet = False
    return check_planet


def check_system(system_address: int, system_name: str) -> bool:
    system_check = True
    data: SystemList = this.sql_session_factory.scalar(select(SystemList).where(SystemList.system_id == system_address))
    if not data:
        data = SystemList(system_id=system_address, system_name=system_name)
        this.sql_session_factory.add(data)
        this.sql_session_factory.commit()
        system_check = False
    return system_check


def name_system(system_id: int) -> str:
    data: SystemList = this.sql_session_factory.scalar(select(SystemList).where(SystemList.system_id == system_id))
    if not data:
        return 'None'
    return data.system_name


def name_planet(system_id: int, planet_id: int) -> str:
    data: PlanetBioSAA = this.sql_session_factory.scalar(select(PlanetBioSAA).where(PlanetBioSAA.system_id == system_id)
                                                         .where(PlanetBioSAA.planet_id == planet_id))
    if data:
        return data.planet_name
    return 'id {str(planet_id)}'


def set_bio(system_id: int, planet_id: int, bio_codex: str, bio_name: str):
    data: BioList = this.sql_session_factory.scalar(select(BioList).where(BioList.system_id == system_id)
                                                    .where(BioList.planet_id == planet_id)
                                                    .where(BioList.bio_codex == bio_codex)
                                                    .where(BioList.bio_name == bio_name)
                                                    )
    if not data:
        data = BioList(system_id=system_id, planet_id=planet_id, bio_codex=bio_codex, bio_name=bio_name)
        this.sql_session_factory.add(data)
        this.sql_session_factory.commit() 


def sell_bio(system_id: int, planet_id: int, bio_codex: str, bio_name: str, bio_cost: int):
    bio_time = datetime.datetime.now()
    bio_time = bio_time.strftime('%Y_%m_%d_%H_%M')
    data = BioShell(system_id=system_id, planet_id=planet_id, bio_codex=bio_codex, 
                    bio_name=bio_name, bio_cost=bio_cost, bio_time=bio_time)
    this.sql_session_factory.add(data)
    this.sql_session_factory.commit() 


def get_bio_cost(bio_codex: str) -> int: 
    price = 0
    data: BioListCost = this.sql_session_factory.scalar(select(BioListCost).where(BioListCost.bio_codex == bio_codex))
    if data:
        price = data.bio_cost
        stmt = update(BioListCost).where(BioListCost.bio_codex == data.bio_codex).values(bio_find=1)
        this.sql_session_factory.execute(stmt)
        this.sql_session_factory.commit()
    return price


def thargoid_add(thargoid_reward: int, thargoid_name: str, thargoid_time: str):
    data = ThargoidList(thargoid_reward=thargoid_reward, thargoid_name=thargoid_name, thargoid_time=thargoid_time)
    this.sql_session_factory.add(data)
    this.sql_session_factory.commit()


def set_market(market_id: int, trade: str) -> int:
    data: MarketList = this.sql_session_factory.scalar(select(MarketList).where(MarketList.market_id == market_id))
    count = 0
    if not data:
        data = MarketList(market_id=market_id, trade=trade)
        this.sql_session_factory.add(data)
        this.sql_session_factory.commit() 
        count = 1
    return count


def get_market_count() -> int:

    return this.sql_session_factory.query(func.count(MarketList.id)).scalar()


def set_docked_fleet(market_id: int):
    data: DockedFleet = this.sql_session_factory.scalar(select(DockedFleet).where(DockedFleet.market_id == market_id))
    if not data:
        data = DockedFleet(market_id=market_id)
        this.sql_session_factory.add(data)
        this.sql_session_factory.commit() 


def get_docked_fleet(market_id: int) -> bool:
    find_fleet = False
    data: DockedFleet = this.sql_session_factory.scalar(select(DockedFleet).where(DockedFleet.market_id == market_id))
    if not data:
        find_fleet = True
    return find_fleet    


def export_bio_lost() -> None:
    if this.sql_session_factory.query(func.count(BioShell.id)).scalar() > 0:
        export_path = config.app_dir_path / 'data_lost'
        if not export_path.exists():
            os.makedirs(export_path)
        stamp_time = datetime.datetime.now()
        stamp_time = stamp_time.strftime('%Y_%m_%d_%H_%M')
        filename = 'bio_' + stamp_time + '.txt'
        file = open(export_path / filename, 'w')
        table = this.sql_session_factory.query(BioShell).all()
        for data in table:
            text_exp = '{} | Name: {} | cost: {} |'.format(data.bio_time, data.bio_name, str(data.bio_cost))
            text_exp += ' System: {} |'.format(name_system(data.system_id))
            text_exp += ' Planet: {}'.format(name_planet(data.system_id, data.planet_id))
            file.write(text_exp + '\n')
        file.close()
