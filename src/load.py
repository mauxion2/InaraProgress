"""
EDMC Inara Progress Plugin
Copyright (c) 2024  Mario Spark , ALl Rights Reserved
Project based on EDMC Rank Progress Plugin Copyright (c) 2021 Seth Osher
Using StatusFlags and overlay from project  BioScan plugin for EDMC Copyright (C) 2023 Jeremy Rimpo
Licensed under the [GNU Public License (GPL)](http://www.gnu.org/licenses/gpl-2.0.html) version 2 or later.

TODO

    2 decorated hero  value x2 x3 itp. zapis do bazy
    3 
    4 sprawdzic sprzedaz jezeli sa   kill_bonds_foot i kill_bonds jednoczesnie
    5 trader sprzedaz commodities update_market  po typie oraz profit z miningu
    6 dodac system do tabeli market powiazac z jump plug.curent_system dodac w parsing

"""
# Core imports
import math
import semantic_version
import requests
import datetime
from typing import Any, MutableMapping, Mapping


# TKinter imports
import tkinter as tk
from tkinter import ttk, colorchooser as tkColorChooser

# EDMC imports
import myNotebook as Nb
from config import config
from theme import theme
from ttkHyperlinkLabel import HyperlinkLabel

# Database objects
from sqlalchemy.orm import Session


from data_progress import data_db
from data_progress.journal_read import parse_journals

# Local imports
from inara_progress import const, overlay
from inara_progress.progresslog import ProgressLog
from inara_progress.status_flags import StatusFlags2  # , StatusFlags
from inara_progress.findpr import check_limit, check_threshold, check_tier


HUNTER_TARG = 4500000
SCOUT2_TARG = 75000
SCOUT1_TARG = 65000

BANSHEES_TARG = 1000000 
REVENANT_TARG = 25000 

HYDRA_TARG = 60000000
ORTHRUS_TARG = 15000000
MEDUSA_TARG = 40000000
BASILISK_TARG = 24000000
CYCLOPS_TARG = 8000000


""" 
17-12-2023 inara start

31-01-2023  15-17godz
Thargoid Type     Pre-Update 14.02    Post Update 14.02
Scout (Marauder)            80,000 →     65,000
Scout (Other variants)      80,000 →     75,000
Cyclops                  8,000,000 →  6,500,000 
Basilisk                24,000,000 → 20,000,000
Medusa                  40,000,000 → 34,000,000
Hydra                   60,000,000 → 50,000,000
Orthrus                 30,000,000 → 40,000,000

    28-05-2024 Update 18.06 

    Cyclops   6,500,000 →  8,000,000
    Basilisk 20,000,000 → 24,000,000
    Medusa   34,000,000 → 40,000,000
    Hydra    50,000,000 → 60,000,000
    Orthrus  40,000,000 → 15,000,000
"""


class InaraProgress:

    def __init__(self) -> None:
        self.NAME = const.plugin_name
        self.VERSION = semantic_version.Version(const.plugin_version)

        self.tab_values = dict()
        self.On_Foot: bool = False
        self.Zero: int = 0
        self.sql_session: Session | None = None
        self.overlay = overlay.Overlay()
        self.use_overlay: tk.BooleanVar | None = None
        self.overlay_color: tk.StringVar | None = None
        self.overlay_anchor_x: tk.IntVar | None = None
        self.overlay_anchor_y: tk.IntVar | None = None
        self.overlay_info_x: tk.IntVar | None = None
        self.overlay_info_y: tk.IntVar | None = None   

        self.parent: tk.Frame | None = None
        self.frame: tk.Frame | None = None
        self.button: ttk.Button | None = None
        self.update_button: HyperlinkLabel | None = None
        self.show_rank: tk.BooleanVar | None = None
        self.show_combat_stats: tk.BooleanVar | None = None
        self.show_trade_stats: tk.BooleanVar | None = None
        self.show_exobiologist_progress: tk.BooleanVar | None = None
        self.show_mercenary_progress: tk.BooleanVar | None = None
        self.show_samaritan_progress: tk.BooleanVar | None = None
        self.show_miner_progress: tk.BooleanVar | None = None        
        self.show_thargoid_progress: tk.BooleanVar | None = None
        self.show_v_stats: tk.BooleanVar | None = None
        self.show_Traveller: tk.BooleanVar | None = None
        self.show_Explorer: tk.BooleanVar | None = None
        self.show_Trader: tk.BooleanVar | None = None
        self.show_Captain: tk.BooleanVar | None = None
        self.show_dh_progress: tk.BooleanVar | None = None
        self.clear_data_db: tk.BooleanVar | None = None

        # Ranks
        self.combat: int = 0
        self.trade: int = 0
        self.explore: int = 0
        self.soldier: int = 0
        self.exobiologist: int = 0
        self.cqc: int = 0
        self.empire: int = 0
        self.federation: int = 0

        self.combat_rank: int = 0
        self.trade_rank: int = 0
        self.explore_rank: int = 0
        self.soldier_rank: int = 0
        self.exobiologist_rank: int = 0
        self.cqc_rank: int = 0
        self.empire_rank: int = 0
        self.federation_rank: int = 0

        # Awards
        self.hunting_bonds: int = 0
        self.hunting_bonds_profit: int = 0
        self.hunting_bonds_tosell: int = 0
        self.hunting_kill: int = 0

        self.combat_bonds: int = 0
        self.combat_profit: int = 0
        self.combat_last_sum: int = 0
        self.kill_bonds: int = 0
        self.kill_bonds_foot: int = 0
        self.soldier_bonds: int = 0
        self.soldier_profit: int = 0
        self.soldier_last_sum: int = 0
        self.soldier_Total_Wins: int = 0
        self.soldier_High_Wins: int = 0
        self.soldier_Settlement: int = 0

        self.exobiologist_Organic: int = 0
        self.exobiologist_Planets: int = 0
        self.exobiologist_Unique: int = 0
        self.rescue_Traded: int = 0
        self.rescue_FireOut: int = 0
        self.rescue_Reboot: int = 0
        self.exploration_Distance: int = 0
        self.exploration_Distance_f: float = 0.0
        self.exploration_Jumps: int = 0
        self.exploration_Visited: int = 0
        self.exploration_L3scan: int = 0
        self.passengers_Delivered: int = 0
        self.passengers_VIP: int = 0
        self.trading_Resources: int = 0
        self.trading_Markets: int = 0
        self.miner_refined: int = 0

        # Thargoid
        self.thargoid_kill: int = 0
        self.thargoid_cyclops: int = 0
        self.thargoid_basilisk: int = 0
        self.thargoid_medusa: int = 0
        self.thargoid_hydra: int = 0
        self.thargoid_scout: int = 0
        self.thargoid_hunter: int = 0

        # Profit All Trade
        self.trade_profit: int = 0
        self.explore_profit: int = 0
        self.bio_profit: int = 0
        self.bio_sell: int = 0
        self.bio_find: int = 0
        self.miner_profit: int = 0

        self.wyd_il: int = 0
        self.curent_system: int = 0

        self.frame = None
        self.labels = dict()


plug = InaraProgress()
LOG = ProgressLog()


def setup_frame_new():
    frame = plug.frame
    for widget in frame.winfo_children():
        widget.destroy()

    border = 0
    styl = ttk.Style()
    thm = config.get_int("theme")
    if thm == 0:
        styl.configure('ed.TSeparator', background=styl.lookup('TLabel', 'foreground'))
    else:
        styl.configure('ed.TSeparator', background=config.get_str('dark_text'))

    frame.columnconfigure(0, weight=1, uniform="a")
    frame.columnconfigure(1, weight=1, uniform="a")
    frame.grid(columnspan=2)

    frame_rank = tk.Frame(frame, borderwidth=border, relief="groove")
    frame_rank.columnconfigure(0, weight=1)  # , uniform="r")
    frame_rank.columnconfigure(1, weight=1)  # , uniform="r")
    frame_rank.columnconfigure(2, weight=1)  # , uniform="r")
    frame_rank.columnconfigure(3, weight=1)  # , uniform="r")
    frame_rank.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

    frame_p = tk.Frame(frame, borderwidth=border, relief="groove")
    frame_p.columnconfigure(0, weight=1)
    frame_p.columnconfigure(1, weight=1, uniform="v")
    frame_p.columnconfigure(2, weight=1, uniform="v")
    frame_p.columnconfigure(3, weight=1, uniform="v")
    frame_p.grid(row=1, column=0, columnspan=2, sticky=tk.EW)

    frame_targ = tk.Frame(frame, borderwidth=border, relief="groove")
    frame_targ.columnconfigure(0, weight=1)
    frame_targ.columnconfigure(1, weight=1, uniform="v")
    frame_targ.columnconfigure(2, weight=1, uniform="v")
    frame_targ.columnconfigure(3, weight=1, uniform="v")
    frame_targ.grid(row=2, column=0, columnspan=2, sticky=tk.EW)

    frame_trade = tk.Frame(frame, borderwidth=border, relief="groove")
    frame_trade.columnconfigure(0, weight=1)
    frame_trade.columnconfigure(1, weight=1, uniform="v")
    frame_trade.columnconfigure(2, weight=0)
    frame_trade.columnconfigure(3, weight=1, uniform="v")
    frame_trade.columnconfigure(4, weight=1, uniform="v")
    frame_trade.grid(row=3, column=0, columnspan=2, sticky=tk.EW)

    plug.labels = dict()
    plug.labels["com"] = (tk.Label(frame_rank),)  # combat
    plug.labels["trd"] = (tk.Label(frame_rank),)  # trade
    plug.labels["exp"] = (tk.Label(frame_rank),)  # exploration
    plug.labels["merc"] = (tk.Label(frame_rank),)  # mercenary
    plug.labels["exo"] = (tk.Label(frame_rank),)  # exobiology
    plug.labels["cqc"] = (tk.Label(frame_rank),)  # cqc
    plug.labels["emp"] = (tk.Label(frame_rank),)  # empire
    plug.labels["fed"] = (tk.Label(frame_rank),)  # Federation

    plug.labels["bounty"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))  # Hunter
    plug.labels["bond"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))  # Combat
    plug.labels["cbond"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))  # Comb. OnFoot

    plug.labels["trav_I"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))
    plug.labels["exp_I"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))
    plug.labels["trad_I"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))
    plug.labels["capt_I"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))

    plug.labels["bio_I"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))  # Exobiologist
    plug.labels["mer_I"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))  # Mercenary
    plug.labels["res_I"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))  # Samaritan
    plug.labels["mdh"] = (tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p), tk.Label(frame_p))  # Miner Hero

    plug.labels["tharg1"] = (tk.Label(frame_targ), tk.Label(frame_targ), tk.Label(frame_targ), tk.Label(frame_targ))
    plug.labels["tharg2"] = (tk.Label(frame_targ), tk.Label(frame_targ), tk.Label(frame_targ), tk.Label(frame_targ))

    plug.labels["profit"] = (tk.Label(frame_trade),)  # Trade Profit
    plug.labels["exp_data"] = (tk.Label(frame_trade),)  # Exploration Data
    plug.labels["bio_data"] = (tk.Label(frame_trade),)  # Biology Data
    plug.labels["bio_bonus"] = (tk.Label(frame_trade),)  # Biology Data Bonus

    #  Do we show the ranks?
    if plug.show_rank.get():
        tk.Label(frame_rank, text="Combat", justify="center").grid(row=0, column=0)  # Combat Label
        plug.labels["com"][0].grid(row=1, column=0)  # combat pct
        tk.Label(frame_rank, text="Trade", justify="center").grid(row=0, column=1)  # trade label
        plug.labels["trd"][0].grid(row=1, column=1)
        tk.Label(frame_rank, text="Exploration", justify="center").grid(row=0, column=2)  # Exploration
        plug.labels["exp"][0].grid(row=1, column=2)
        tk.Label(frame_rank, text="Mercenary", justify="center").grid(row=0, column=3)  # Mercenary label
        plug.labels["merc"][0].grid(row=1, column=3)  # merc pct
        tk.Label(frame_rank, text="Exobiology", justify="center").grid(row=2, column=0)  # Exobiology
        plug.labels["exo"][0].grid(row=3, column=0)
        tk.Label(frame_rank, text="CQC", justify="center").grid(row=2, column=1)  # CQC
        plug.labels["cqc"][0].grid(row=3, column=1)
        tk.Label(frame_rank, text="Empire", justify="center").grid(row=2, column=2)  # Empire
        plug.labels["emp"][0].grid(row=3, column=2)
        tk.Label(frame_rank, text="Federation", justify="center").grid(row=2, column=3)  # Federation
        plug.labels["fed"][0].grid(row=3, column=3)

    # Do we show combat stats? or trade stats?
    if plug.show_combat_stats.get() or plug.show_trade_stats.get() or plug.show_thargoid_progress.get():
        if plug.show_rank.get():
            separator = ttk.Separator(frame_rank, style='ed.TSeparator', orient=tk.HORIZONTAL)
            separator.grid(row=4, columnspan=4, pady=0, sticky=tk.EW)

        if plug.show_combat_stats.get():
            # Bounties, ToSell, Sum
            tk.Label(frame_p, text="Inara (Tier)", justify="center").grid(row=1, column=0)
            tk.Label(frame_p, text="  Bounty").grid(row=1, column=1, sticky=tk.W)
            tk.Label(frame_p, text="To Sell").grid(row=1, column=2, sticky=tk.W)
            tk.Label(frame_p, text="Sumary Profit").grid(row=1, column=3, sticky=tk.W)
            plug.labels["bounty"][0].grid(row=5, column=0, sticky=tk.W)  # Hunter Bounties
            plug.labels["bounty"][1].grid(row=5, column=1, sticky=tk.W)
            plug.labels["bounty"][2].grid(row=5, column=2, sticky=tk.W)
            plug.labels["bounty"][3].grid(row=5, column=3, sticky=tk.W)

            plug.labels["bond"][0].grid(row=6, column=0, sticky=tk.W)  # Combat Bond
            plug.labels["bond"][1].grid(row=6, column=1, sticky=tk.W)
            plug.labels["bond"][2].grid(row=6, column=2, sticky=tk.W)
            plug.labels["bond"][3].grid(row=6, column=3, sticky=tk.W)

            plug.labels["cbond"][0].grid(row=7, column=0, sticky=tk.W)  # Combat Bond OnFoot
            plug.labels["cbond"][1].grid(row=7, column=1, sticky=tk.W)
            plug.labels["cbond"][2].grid(row=7, column=2, sticky=tk.W)
            plug.labels["cbond"][3].grid(row=7, column=3, sticky=tk.W)

            separator = ttk.Separator(frame_p, style='ed.TSeparator', orient=tk.HORIZONTAL)
            separator.grid(row=8, columnspan=4, pady=0, sticky=tk.EW)

        if (plug.show_v_stats.get() and plug.show_Traveller.get() and
                plug.show_Explorer.get() and plug.show_Trader.get() and plug.show_Captain.get()):

            plug.labels["trav_I"][0].grid(row=10, column=0)
            plug.labels["trav_I"][1].grid(row=11, column=0)
            plug.labels["trav_I"][2].grid(row=12, column=0)

            plug.labels["exp_I"][0].grid(row=10, column=1)
            plug.labels["exp_I"][1].grid(row=11, column=1)
            plug.labels["exp_I"][2].grid(row=12, column=1)

            plug.labels["trad_I"][0].grid(row=10, column=2)
            plug.labels["trad_I"][1].grid(row=11, column=2)
            plug.labels["trad_I"][2].grid(row=12, column=2)

            plug.labels["capt_I"][0].grid(row=10, column=3)
            plug.labels["capt_I"][1].grid(row=11, column=3)
            plug.labels["capt_I"][2].grid(row=12, column=3)

        else:
            if plug.show_Traveller.get():
                plug.labels["trav_I"][0].grid(row=10, column=0)
                plug.labels["trav_I"][1].grid(row=10, column=1)
                plug.labels["trav_I"][2].grid(row=10, column=2)

            if plug.show_Explorer.get():
                plug.labels["exp_I"][0].grid(row=11, column=0)
                plug.labels["exp_I"][1].grid(row=11, column=1)
                plug.labels["exp_I"][2].grid(row=11, column=2)

            if plug.show_Trader.get():
                plug.labels["trad_I"][0].grid(row=12, column=0)
                plug.labels["trad_I"][1].grid(row=12, column=1)
                plug.labels["trad_I"][2].grid(row=12, column=2)

            if plug.show_Captain.get():
                plug.labels["capt_I"][0].grid(row=13, column=0)
                plug.labels["capt_I"][1].grid(row=13, column=1)
                plug.labels["capt_I"][2].grid(row=13, column=2)

        if (plug.show_Traveller.get() or plug.show_Explorer.get() or 
                plug.show_Trader.get() or plug.show_Captain.get()):
            separator = ttk.Separator(frame_p, style='ed.TSeparator', orient=tk.HORIZONTAL)
            separator.grid(row=15, columnspan=4, pady=0, sticky=tk.EW)

        if plug.show_exobiologist_progress.get():
            plug.labels["bio_I"][0].grid(row=17, column=0, sticky=tk.W)  # Exobiologist Inara
            plug.labels["bio_I"][1].grid(row=17, column=1)
            plug.labels["bio_I"][2].grid(row=17, column=2)
            plug.labels["bio_I"][3].grid(row=17, column=3)

        if plug.show_mercenary_progress.get():
            plug.labels["mer_I"][0].grid(row=18, column=0, sticky=tk.W)  # Mercenary Inara
            plug.labels["mer_I"][1].grid(row=18, column=1)
            plug.labels["mer_I"][2].grid(row=18, column=2)
            plug.labels["mer_I"][3].grid(row=18, column=3)

        if plug.show_samaritan_progress.get():
            plug.labels["res_I"][0].grid(row=19, column=0, sticky=tk.W)  # Samaritan Inara
            plug.labels["res_I"][1].grid(row=19, column=1)
            plug.labels["res_I"][2].grid(row=19, column=2)
            plug.labels["res_I"][3].grid(row=19, column=3)

        if plug.show_miner_progress.get():
            plug.labels["mdh"][0].grid(row=20, column=0, sticky=tk.W)  # Miner Inara
            plug.labels["mdh"][1].grid(row=20, column=1)
            if plug.show_dh_progress.get():
                plug.labels["mdh"][2].grid(row=20, column=2, sticky=tk.W)  # Decorated Hero Inara
                plug.labels["mdh"][3].grid(row=20, column=3)
        else:
            if plug.show_dh_progress.get():
                plug.labels["mdh"][2].grid(row=20, column=0, sticky=tk.W)  # Decorated Hero Inara
                plug.labels["mdh"][3].grid(row=20, column=1)

        if (plug.show_exobiologist_progress.get() or plug.show_mercenary_progress.get() or 
                plug.show_samaritan_progress.get() or plug.show_miner_progress.get() or 
                plug.show_dh_progress.get()) and (plug.show_thargoid_progress.get() or plug.show_trade_stats.get()):
            separator = ttk.Separator(frame_p, style='ed.TSeparator', orient=tk.HORIZONTAL)
            separator.grid(row=21, columnspan=4, pady=0, sticky=tk.EW)

        if plug.show_thargoid_progress.get():
            plug.labels["tharg1"][0].grid(row=25, column=0, sticky=tk.W)
            plug.labels["tharg1"][1].grid(row=25, column=1)
            plug.labels["tharg1"][2].grid(row=25, column=2)
            plug.labels["tharg1"][3].grid(row=25, column=3)
            plug.labels["tharg2"][0].grid(row=26, column=0, sticky=tk.W)
            plug.labels["tharg2"][1].grid(row=26, column=1)
            plug.labels["tharg2"][2].grid(row=26, column=2)
            plug.labels["tharg2"][3].grid(row=26, column=3)

            if plug.show_trade_stats.get():
                separator = ttk.Separator(frame_targ, style='ed.TSeparator', orient=tk.HORIZONTAL)
                separator.grid(row=30, columnspan=4, pady=0, sticky=tk.EW)

        if plug.show_trade_stats.get():
            tk.Label(frame_trade, text="Profit Trade:").grid(row=9, column=0, sticky=tk.W)
            plug.labels["profit"][0].grid(row=9, column=1, sticky=tk.W)
            tk.Label(frame_trade, text="Exploration Profit").grid(row=9, column=3, sticky=tk.W)
            plug.labels["exp_data"][0].grid(row=9, column=4, sticky=tk.W)
            tk.Label(frame_trade, text="Profit BioData:").grid(row=10, column=0, sticky=tk.W)
            plug.labels["bio_data"][0].grid(row=10, column=1, sticky=tk.W)
            tk.Label(frame_trade, text="BioData To Sell:").grid(row=10, column=3, sticky=tk.W)
            plug.labels["bio_bonus"][0].grid(row=10, column=4, sticky=tk.W)

    for widget in frame.winfo_children():
        theme.update(widget)


def update_color(cl: int, val: int, tab_disp: tk.Label) -> tk.Label:
    style = ttk.Style()
    if cl <= val:
        tab_disp.config(fg="green")
    else:
        thm = config.get_int("theme")
        if thm == 0:
            tab_disp.config(fg=style.lookup('TLabel', 'foreground'))
        else:
            tab_disp.config(fg=config.get_str('dark_text'))
    return tab_disp


def update_stats():
    plug.labels["com"][0]["text"] = f"{const.combat_ranks[plug.combat_rank]}  {plug.combat}%"
    plug.labels["trd"][0]["text"] = f"{const.trade_ranks[plug.trade_rank]}  {plug.trade}%"
    plug.labels["exp"][0]["text"] = f"{const.explore_ranks[plug.explore_rank]}  {plug.explore}%"
    plug.labels["merc"][0]["text"] = f"{const.soldier_ranks[plug.soldier_rank]}  {plug.soldier}%"

    plug.labels["exo"][0]["text"] = f"{const.exobiologist_ranks[plug.exobiologist_rank]}  {plug.exobiologist}%"
    plug.labels["cqc"][0]["text"] = f"{const.cqc_ranks[plug.cqc_rank]}  {plug.cqc}%"
    plug.labels["emp"][0]["text"] = f"{const.empire_ranks[plug.empire_rank]}  {plug.empire}%"
    plug.labels["fed"][0]["text"] = f"{const.federation_ranks[plug.federation_rank]}  {plug.federation}%"

    config_rank_set()
    update_display()


def update_display(overlay_info: str = "", overlay_info_change: bool = False):
    if plug.show_trade_stats.get():
        plug.labels["profit"][0]["text"] = "{:,} Cr".format(plug.trade_profit)
        plug.labels["exp_data"][0]["text"] = "{:,} Cr".format(plug.explore_profit)
        plug.labels["bio_data"][0]["text"] = "{:,} Cr".format(plug.bio_profit)
        plug.labels["bio_bonus"][0]["text"] = "{} / {:,} Cr".format(plug.bio_find, plug.bio_sell)

    if plug.show_combat_stats.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.hunting_bonds

        plug.labels["bounty"][0]["text"] = "Hunter (tier {}):".format(check_tier(const.Hunter_Inara, plug.tab_values))
        plug.labels["bounty"][1]["text"] = "{:,} / {:,}".format(plug.hunting_bonds,
                                                                check_threshold(plug.hunting_bonds,
                                                                                const.Hunter_Inara, "Bonds")
                                                                )
        plug.labels["bounty"][2]["text"] = "{} / {:,} Cr".format(plug.hunting_kill, plug.hunting_bonds_tosell)
        plug.labels["bounty"][3]["text"] = "{:,} Cr".format(plug.hunting_bonds_profit)

        plug.labels["bond"][0]["text"] = "{}".format("Combat OnFoot:" if plug.On_Foot else "Combat :")
        plug.labels["bond"][1]["text"] = f"[{plug.combat_bonds}]   [{plug.soldier_bonds}]"
        plug.labels["bond"][2]["text"] = "{} / {:,} Cr".format(plug.kill_bonds, plug.combat_last_sum)
        plug.labels["bond"][3]["text"] = "{:,} Cr".format(plug.combat_profit)

        bonds_sum = plug.combat_bonds + plug.soldier_bonds
        plug.tab_values.clear()
        plug.tab_values[0] = bonds_sum
        plug.labels["cbond"][0]["text"] = "Soldier (tier {}) :".format(check_tier(const.Soldier_Inara, plug.tab_values))
        plug.labels["cbond"][1]["text"] = "{:,} / {:,}".format(bonds_sum,
                                                               check_threshold(bonds_sum,
                                                                               const.Soldier_Inara, "Bonds")
                                                               )
        plug.labels["cbond"][2]["text"] = "{} / {:,} Cr".format(plug.kill_bonds_foot, plug.soldier_last_sum)
        plug.labels["cbond"][3]["text"] = "{:,} Cr".format(plug.soldier_profit)

    #  Begin tabela 4x3
    if plug.show_Traveller.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.exploration_Distance
        plug.tab_values[1] = plug.exploration_Jumps
        min_tier = check_tier(const.Traveller_Inara, plug.tab_values)
        mer1 = check_limit(const.Traveller_Inara, "Distance", min_tier)
        mer2 = check_limit(const.Traveller_Inara, "Jumps", min_tier)
        plug.labels["trav_I"] = (plug.labels["trav_I"][0],
                                 update_color(mer1, plug.exploration_Distance, plug.labels["trav_I"][1]),
                                 update_color(mer2, plug.exploration_Jumps, plug.labels["trav_I"][2])
                                 )
        plug.labels["trav_I"][0]["text"] = "Traveller (tier {}) :".format(min_tier)
        plug.labels["trav_I"][1]["text"] = "Distance: {:,}/{:,}".format(plug.exploration_Distance, mer1)
        plug.labels["trav_I"][2]["text"] = "Jumps: {:,}/{:,}".format(plug.exploration_Jumps, mer2)

    if plug.show_Explorer.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.exploration_Visited
        plug.tab_values[1] = plug.exploration_L3scan
        min_tier = check_tier(const.Explorer_Inara, plug.tab_values)
        mer1 = check_limit(const.Explorer_Inara, "Visited", min_tier)
        mer2 = check_limit(const.Explorer_Inara, "L3scans", min_tier)
        plug.labels["exp_I"] = (plug.labels["exp_I"][0],
                                update_color(mer1, plug.exploration_Visited, plug.labels["exp_I"][1]),
                                update_color(mer2, plug.exploration_L3scan, plug.labels["exp_I"][2])
                                )
        plug.labels["exp_I"][0]["text"] = "Explorer (tier {}) :".format(min_tier)
        plug.labels["exp_I"][1]["text"] = "Visited: {:,}/{:,}".format(plug.exploration_Visited, mer1)
        plug.labels["exp_I"][2]["text"] = "L3 Scans: {:,}/{:,}".format(plug.exploration_L3scan, mer2)
 
    if plug.show_Trader.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.trading_Resources
        plug.tab_values[1] = plug.trading_Markets
        min_tier = check_tier(const.Trader_Inara, plug.tab_values)
        mer1 = check_limit(const.Trader_Inara, "Commodities", min_tier)
        mer2 = check_limit(const.Trader_Inara, "Market", min_tier)
        plug.labels["trad_I"] = (plug.labels["trad_I"][0],
                                 update_color(mer1, plug.trading_Resources, plug.labels["trad_I"][1]),
                                 update_color(mer2, plug.trading_Markets, plug.labels["trad_I"][2])
                                 )
        plug.labels["trad_I"][0]["text"] = "Trader (tier {}) :".format(min_tier)
        plug.labels["trad_I"][1]["text"] = "Resources: {:,}/{:,}".format(plug.trading_Resources, mer1)
        plug.labels["trad_I"][2]["text"] = "Market: {:,}/{:,}".format(plug.trading_Markets, mer2)

    if plug.show_Captain.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.passengers_Delivered
        plug.tab_values[1] = plug.passengers_VIP
        min_tier = check_tier(const.Captain_Inara, plug.tab_values)
        mer1 = check_limit(const.Captain_Inara, "Passengers", min_tier)
        mer2 = check_limit(const.Captain_Inara, "VIPs", min_tier)
        plug.labels["capt_I"] = (plug.labels["capt_I"][0],
                                 update_color(mer1, plug.passengers_Delivered, plug.labels["capt_I"][1]),
                                 update_color(mer2, plug.passengers_VIP, plug.labels["capt_I"][2])
                                 )
        plug.labels["capt_I"][0]["text"] = "Captain (tier {}) :".format(min_tier)
        plug.labels["capt_I"][1]["text"] = "Tourists: {:,}/{:,}".format(plug.passengers_Delivered, mer1)
        plug.labels["capt_I"][2]["text"] = "VIPs : {:,}/{:,}".format(plug.passengers_VIP, mer2)
    #  End Tabela 4x3

    if plug.show_exobiologist_progress.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.exobiologist_Organic
        plug.tab_values[1] = plug.exobiologist_Planets
        plug.tab_values[2] = plug.exobiologist_Unique
        min_tier = check_tier(const.Exobiologist_Inara, plug.tab_values)
        mer1 = check_limit(const.Exobiologist_Inara, "Organic", min_tier)
        mer2 = check_limit(const.Exobiologist_Inara, "Planets", min_tier)
        mer3 = check_limit(const.Exobiologist_Inara, "Unique", min_tier)
        plug.labels["bio_I"] = (plug.labels["bio_I"][0],
                                update_color(mer1, plug.exobiologist_Organic, plug.labels["bio_I"][1]),
                                update_color(mer2, plug.exobiologist_Planets, plug.labels["bio_I"][2]),
                                update_color(mer3, plug.exobiologist_Unique, plug.labels["bio_I"][3])
                                )
        plug.labels["bio_I"][0]["text"] = "Exobiologist (tier {}) :".format(min_tier)
        plug.labels["bio_I"][1]["text"] = "Organic: {:,}/{:,}".format(plug.exobiologist_Organic, mer1)
        plug.labels["bio_I"][2]["text"] = "Planets: {:,}/{:,}".format(plug.exobiologist_Planets, mer2)
        plug.labels["bio_I"][3]["text"] = "Unique: {:,}/{:,}".format(plug.exobiologist_Unique, mer3)

    if plug.show_mercenary_progress.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.soldier_Total_Wins
        plug.tab_values[1] = plug.soldier_High_Wins
        plug.tab_values[2] = plug.soldier_Settlement
        min_tier = check_tier(const.Mercenary_Inara, plug.tab_values)
        mer1 = check_limit(const.Mercenary_Inara, "Swon", min_tier)
        mer2 = check_limit(const.Mercenary_Inara, "Hwon", min_tier)
        mer3 = check_limit(const.Mercenary_Inara, "settlements", min_tier)
        plug.labels["mer_I"] = (plug.labels["mer_I"][0],
                                update_color(mer1, plug.soldier_Total_Wins, plug.labels["mer_I"][1]),
                                update_color(mer2, plug.soldier_High_Wins, plug.labels["mer_I"][2]),
                                update_color(mer3, plug.soldier_Settlement, plug.labels["mer_I"][3])
                                )
        plug.labels["mer_I"][0]["text"] = "Mercenary (tier {}) :".format(min_tier)
        plug.labels["mer_I"][1]["text"] = "Total Wins: {:,}/{:,}".format(plug.soldier_Total_Wins, mer1)
        plug.labels["mer_I"][2]["text"] = "High Wins: {:,}/{:,}".format(plug.soldier_High_Wins, mer2)
        plug.labels["mer_I"][3]["text"] = "Colony A.D.: {:,}/{:,}".format(plug.soldier_Settlement, mer3)

    if plug.show_samaritan_progress.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.rescue_Traded
        plug.tab_values[1] = plug.rescue_Reboot
        plug.tab_values[2] = plug.rescue_FireOut
        min_tier = check_tier(const.Samaritan_Inara, plug.tab_values)
        mer1 = check_limit(const.Samaritan_Inara, "Rescued", min_tier)
        mer2 = check_limit(const.Samaritan_Inara, "Rebooted", min_tier)
        mer3 = check_limit(const.Samaritan_Inara, "Fires", min_tier)
        plug.labels["res_I"] = (plug.labels["res_I"][0],
                                update_color(mer1, plug.rescue_Traded, plug.labels["res_I"][1]),
                                update_color(mer2, plug.rescue_Reboot, plug.labels["res_I"][2]),
                                update_color(mer3, plug.rescue_FireOut, plug.labels["res_I"][3])
                                )
        plug.labels["res_I"][0]["text"] = "Samaritan (tier {}) :".format(min_tier)
        plug.labels["res_I"][1]["text"] = "Rescued: {:,}/{:,}".format(plug.rescue_Traded, mer1)
        plug.labels["res_I"][2]["text"] = "Reboot: {:,}/{:,}".format(plug.rescue_Reboot, mer2)
        plug.labels["res_I"][3]["text"] = "FireOut: {:,}/{:,}".format(plug.rescue_FireOut, mer3)

    if plug.show_miner_progress.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.miner_refined
        plug.labels["mdh"][0]["text"] = "Miner (tier {}):".format(check_tier(const.Miner_Inara, plug.tab_values))
        plug.labels["mdh"][1]["text"] = "{:,}/{:,}".format(plug.miner_refined,
                                                           check_threshold(plug.miner_refined,
                                                                           const.Miner_Inara, "Refined")
                                                           )
    
    if plug.show_dh_progress.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.Zero
        plug.labels["mdh"][2]["text"] = "Decorated Hero (tier {}):".format(check_tier(const.Hero_Inara,
                                                                                      plug.tab_values)
                                                                           )
        plug.labels["mdh"][3]["text"] = "{:,}/{:,}".format(plug.Zero, 
                                                           check_threshold(plug.Zero, const.Hero_Inara, "Tier_5"))

    if plug.show_thargoid_progress.get():
        plug.tab_values.clear()
        plug.tab_values[0] = plug.thargoid_kill
        plug.tab_values[1] = plug.thargoid_cyclops
        plug.tab_values[2] = plug.thargoid_basilisk
        plug.tab_values[3] = plug.thargoid_medusa
        plug.tab_values[4] = plug.thargoid_hydra
        min_tier = check_tier(const.Xeno_Inara, plug.tab_values)
        mer1 = check_limit(const.Xeno_Inara, "Killed", min_tier)
        mer2 = check_limit(const.Xeno_Inara, "Interceptors", min_tier)
        mer3 = check_limit(const.Xeno_Inara, "Basilisk", min_tier)
        mer4 = check_limit(const.Xeno_Inara, "Medusa", min_tier)
        mer5 = check_limit(const.Xeno_Inara, "Hydra", min_tier)
        plug.labels["tharg1"] = (plug.labels["tharg1"][0],
                                 update_color(mer2, plug.thargoid_cyclops, plug.labels["tharg1"][1]),
                                 update_color(mer3, plug.thargoid_basilisk, plug.labels["tharg1"][2]),
                                 update_color(mer4, plug.thargoid_medusa, plug.labels["tharg1"][3])
                                 )
        plug.labels["tharg2"] = (update_color(mer1, plug.thargoid_kill, plug.labels["tharg2"][0]),
                                 update_color(mer5, plug.thargoid_hydra, plug.labels["tharg2"][1]),
                                 plug.labels["tharg2"][2],
                                 plug.labels["tharg2"][3]
                                 )
        plug.labels["tharg1"][0]["text"] = "Xeno-hunter (tier {}) :".format(min_tier)
        plug.labels["tharg1"][1]["text"] = "Interceptors: {:,}/{:,}".format(plug.thargoid_cyclops, mer2)
        plug.labels["tharg1"][2]["text"] = "Basilisk: {:,}/{:,}".format(plug.thargoid_basilisk, mer3)
        plug.labels["tharg1"][3]["text"] = "Medusa: {:,}/{:,}".format(plug.thargoid_medusa, mer4)

        plug.labels["tharg2"][0]["text"] = "Killed: {:,}/{:,}".format(plug.thargoid_kill, mer1)
        plug.labels["tharg2"][1]["text"] = "Hydra: {:,}/{:,}".format(plug.thargoid_hydra, mer5)
        plug.labels["tharg2"][2]["text"] = "Hunter: {}".format(plug.thargoid_hunter)
        plug.labels["tharg2"][3]["text"] = "Scout: {}".format(plug.thargoid_scout)

    if plug.use_overlay.get() and plug.overlay.available():
    
        overlay_text = "" 
        overlay_text += "BioData To Sell: {} / {:,} Cr \n".format(plug.bio_find, plug.bio_sell)
        overlay_text += "Soldier {} / {:,} Cr\n".format(plug.kill_bonds_foot, plug.soldier_last_sum) 
        overlay_text += "Combat {} / {:,} Cr\n".format(plug.kill_bonds, plug.combat_last_sum)
        overlay_text += "Hunter {} / {:,} Cr\n".format(plug.hunting_kill, plug.hunting_bonds_tosell)
        # overlay_text += "Trade Profit {:,}\n".format(plug.trade_profit)
        # overlay_text += "Community {:,} \n".format(plug.wyd_il)

        plug.overlay.display('inaraprogress_display', overlay_text, plug.overlay_anchor_x.get(),
                             plug.overlay_anchor_y.get(), plug.overlay_color.get(), 'normal')

        if overlay_info_change:

            plug.overlay.draw('inaraprogress_info', overlay_info, plug.overlay_info_x.get(), 
                              plug.overlay_info_y.get(), plug.overlay_color.get(), 'large', 6)


def update_progress(entry):
    if "Combat" in entry:
        plug.combat = entry["Combat"]
    if "Trade" in entry:
        plug.trade = entry["Trade"]
    if "Explore" in entry:
        plug.explore = entry["Explore"]
    if "Soldier" in entry:
        plug.soldier = entry["Soldier"]
    if "Exobiologist" in entry:
        plug.exobiologist = entry["Exobiologist"]
    if "CQC" in entry:
        plug.cqc = entry["CQC"]
    if "Empire" in entry:
        plug.empire = entry["Empire"]
    if "Federation" in entry:
        plug.federation = entry["Federation"]

    update_stats()


def update_ranks(entry):
    if "Combat" in entry:
        plug.combat_rank = entry["Combat"]
    if "Trade" in entry:
        plug.trade_rank = entry["Trade"]
    if "Explore" in entry:
        plug.explore_rank = entry["Explore"]
    if "Soldier" in entry:
        plug.soldier_rank = entry["Soldier"]
    if "Exobiologist" in entry:
        plug.exobiologist_rank = entry["Exobiologist"]
    if "CQC" in entry:
        plug.cqc_rank = entry["CQC"]
    if "Empire" in entry:
        plug.empire_rank = entry["Empire"]
    if "Federation" in entry:
        plug.federation_rank = entry["Federation"]

    update_stats()


def update_promotion(entry):
    if "Combat" in entry:
        plug.combat_rank = entry["Combat"]
        plug.combat = 0
    if "Trade" in entry:
        plug.trade_rank = entry["Trade"]
        plug.trade = 0
    if "Explore" in entry:
        plug.explore_rank = entry["Explore"]
        plug.explore = 0
    if "Soldier" in entry:
        plug.soldier_rank = entry["Soldier"]
        plug.soldier = 0
    if "Exobiologist" in entry:
        plug.exobiologist_rank = entry["Exobiologist"]
        plug.exobiologist = 0
    if "CQC" in entry:
        plug.cqc_rank = entry["CQC"]
        plug.cqc = 0
    if "Empire" in entry:
        plug.empire_rank = entry["Empire"]
        plug.empire = 0
    if "Federation" in entry:
        plug.federation_rank = entry["Federation"]
        plug.federation = 0

    update_stats()


#  "event":"Bounty", "Rewards":[ { "Faction":"Nehet Patron's Principles", "Reward":5620 } ],
#                    "Target":"empire_eagle",
#                    "TotalReward":5620,
#                    "VictimFaction":"Nehet Progressive Party"
#                    }
#  "event":"Bounty","Faction":"HIP 18828 Empire Consulate",
#                   "Target":"Skimmer",
#                   "Reward":1000,
#                   "VictimFaction":"HIP 18828 Empire Consulate"


def update_hunter_bounty(entry):
    
    total_reward = entry["TotalReward"]
    plug.hunting_bonds_tosell += total_reward
    plug.hunting_kill += 1

    config_value_set()
    update_display("Hunter Kill {:,}".format(plug.hunting_kill), True)


def update_combat_bond(entry):

    if plug.On_Foot:
        plug.soldier_bonds += 1
        plug.kill_bonds_foot += 1
        plug.soldier_last_sum += entry["Reward"]
        overlay_text = "Combat On_Foot {:,}".format(plug.soldier_bonds)
    else:
        plug.combat_bonds += 1
        plug.kill_bonds += 1
        plug.combat_last_sum += entry["Reward"]
        overlay_text = "Combat {:,}".format(plug.combat_bonds)

    if 'VictimFaction_Localised' in entry:
        targ = entry["VictimFaction_Localised"]
        if targ == 'Thargoids':
            plug.thargoid_kill += 1
            reward = entry["Reward"]
            overlay_text += "\nThargoids Kill {:,}".format(plug.thargoid_kill)
            targ_name = 'none name'
            timestamp = entry["timestamp"]   # "timestamp":"2024-05-28T08:00:00Z"
            timestamp = timestamp.replace("T", " ")
            timestamp = timestamp.replace("Z", "")

            if reward == CYCLOPS_TARG:
                plug.thargoid_cyclops += 1
                targ_name = 'Cyclops'
            if reward == BASILISK_TARG:
                plug.thargoid_basilisk += 1
                targ_name = 'Basilisk'
            if reward == MEDUSA_TARG:
                plug.thargoid_medusa += 1
                targ_name = 'Medusa'
            if reward == HYDRA_TARG:
                plug.thargoid_hydra += 1
                targ_name = 'Hydra'
            if reward == SCOUT1_TARG or reward == SCOUT2_TARG:
                plug.thargoid_scout += 1
                targ_name = 'Scout'
            if reward == HUNTER_TARG:
                plug.thargoid_hunter += 1
                targ_name = 'Hunter'
            if reward == ORTHRUS_TARG:
                targ_name = 'Orthrus'
            if reward == BANSHEES_TARG:
                targ_name = 'Banshees'
            if reward == REVENANT_TARG:
                targ_name = 'Revenant'

            data_db.thargoid_add(timestamp, targ_name, reward)

    config_value_set()
    update_display(overlay_text, True)


def update_redeem_voucher(entry):
    type_redeemrvoucher = entry["Type"]
    if 'BrokerPercentage' in entry:  
        corect = 0.75
    else:
        corect = 1

    overlay_text = ''
    if type_redeemrvoucher == 'bounty':
        sell_bonties = entry["Amount"]
        plug.hunting_bonds_profit += sell_bonties
        overlay_text = "Hunting {:,} Cr".format(plug.hunting_bonds_profit)
        sell_bonties = sell_bonties / corect
        if plug.hunting_bonds_tosell > sell_bonties:
            plug.hunting_bonds_tosell -= sell_bonties
            plug.hunting_kill -= 1
            plug.hunting_bonds += 1 
        else:
            plug.hunting_bonds_tosell = 0
            plug.hunting_bonds += plug.hunting_kill
            plug.hunting_kill = 0

    if type_redeemrvoucher == 'CombatBond':
        # sprawdzic sprzedaz jezeli sa   kill_bonds_foot i kill_bonds jednoczesnie
        if plug.kill_bonds_foot > 0:
            sell_bonds = entry["Amount"]
            if plug.kill_bonds > 0:
                sell_bonds -= plug.combat_last_sum * corect
            plug.soldier_profit += sell_bonds
            overlay_text = "Soldier {:,} Cr".format(plug.soldier_profit)
            sell_bonds = sell_bonds / corect
            if sell_bonds < plug.soldier_last_sum:
                plug.soldier_last_sum -= sell_bonds
                plug.kill_bonds_foot -= 1
            else:
                plug.soldier_last_sum = 0
                plug.kill_bonds_foot = 0

        if plug.kill_bonds > 0:
            sell_bonds = entry["Amount"]
            if plug.kill_bonds_foot > 0:
                sell_bonds = plug.combat_last_sum * corect
            plug.combat_profit += sell_bonds
            overlay_text = "Combat {:,} Cr".format(plug.combat_profit)
            sell_bonds = sell_bonds / corect
            if sell_bonds < plug.combat_last_sum:
                plug.combat_last_sum -= sell_bonds
                plug.kill_bonds -= 1
            else:
                plug.combat_last_sum = 0
                plug.kill_bonds = 0

    config_value_set()
    update_display(overlay_text, True)


""""
"event":"MarketSell", "MarketID":128983318, 
        "Type":"osmium", "Count":32, "SellPrice":167641, "TotalSale":5364512, "AvgPricePaid":0 }
"event":"MarketSell", "MarketID":128734402, 
        "Type":"osmium", "Count":40, "SellPrice":203012, "TotalSale":8120480, "AvgPricePaid":100440 }
"event":"MarketSell", "MarketID":3700276224, 
        "Type":"powerconverter", 
        "Type_Localised":"Power Converter", 
        "Count":8, "SellPrice":72, 
        "TotalSale":576, 
        "AvgPricePaid":143500 
        }
"event":"MarketBuy", "MarketID":3705283584, 
        "Type":"osmium", "Count":7, "BuyPrice":61473, "TotalCost":430311 }
"event":"MarketSell", "MarketID":128983318, 
        "Type":"gold", "Count":3, "SellPrice":55985, "TotalSale":167955, "AvgPricePaid":0 }
"event":"MarketSell", "MarketID":128983318, 
        "Type":"silver", "Count":31, "SellPrice":48935, "TotalSale":1516985, "AvgPricePaid":0 }
"event":"MarketSell", "MarketID":128983318, 
        "Type":"palladium", "Count":7, "SellPrice":59149, "TotalSale":414043, "AvgPricePaid":0 }
"event":"MarketSell", "MarketID":128983318, 
        "Type":"platinum", "Count":10, "SellPrice":202450, "TotalSale":2024500, "AvgPricePaid":0 }
"event":"MarketSell", "MarketID":128983318, 
        "Type":"monazite", "Count":15, "SellPrice":356077, "TotalSale":5341155, "AvgPricePaid":0 }
"event":"MarketSell", "MarketID":128983318, 
        "Type":"osmium", "Count":32, "SellPrice":167641, "TotalSale":5364512, "AvgPricePaid":0 }
"""


def community(entry, count_sell):
    if entry["MarketID"] == 3228804352:
        if plug.wyd_il == 0:
            plug.wyd_il = 35695
        plug.wyd_il += count_sell
        config_wyd_set()   


def update_market(entry, is_buy=False):
    # dodac system do tabli market powiazac z jump plug.curent_system dodac w parsing
    timestamp = entry["timestamp"]   # "timestamp":"2024-05-28T08:00:00Z"
    timestamp = timestamp.replace("T", " ")
    timestamp = timestamp.replace("Z", "")
    market = entry["MarketID"]
    if is_buy:
        if data_db.get_docked_fleet(market):   
            plug.trading_Markets += data_db.set_market(plug.curent_system, market, 'buy')

    else:
        if data_db.get_docked_fleet(market):
            overlay_text = ''
            count_sell = entry["Count"]
            pr_cr = count_sell * (entry["SellPrice"] - entry["AvgPricePaid"])
            if pr_cr > 0:
                data_db.set_trade(timestamp, market, pr_cr)
                plug.trade_profit += pr_cr 
                overlay_text = "Trade Profit {:,}\n".format(plug.trade_profit)
            plug.trading_Markets += data_db.set_market(plug.curent_system, market, 'sell')
            plug.trading_Resources += count_sell
            #  selekja sprzedaz typ mining itp..

            overlay_text += "Sumary Resources {:,}".format(plug.trading_Resources)
            config_trade_set()
            update_display(overlay_text, True)


def update_exp_data(entry):
    # add sell system
    plug.explore_profit += entry["TotalEarnings"]
    config_trade_set()
    update_display("Explore Profit {:,}".format(plug.explore_profit), True)


def update_bio_data(entry):
    bio_data_tab = entry["BioData"]
    count_bio = len(bio_data_tab) 
    sell_bio_count = data_db.get_sell_bio_count()
    clear_sell_bio_table = False
    plug.exobiologist_Organic += count_bio
    # jezeli sell_bio_count < od count_bio blad wpisow mozliwe wylaczony plugin

    value_bio = 0
    bonus_bio = 0
    for bio in bio_data_tab:
        value_bio += bio["Value"]
        bonus_bio += bio["Bonus"]
    plug.bio_profit += value_bio + bonus_bio

    if count_bio == sell_bio_count:
        clear_sell_bio_table = True
        plug.bio_sell = 0
        plug.bio_find = 0
    else:    
        plug.bio_sell -= value_bio
        if plug.bio_sell < 0:
            plug.bio_sell = 0 

        plug.bio_find -= count_bio
        if plug.bio_find < 0:
            plug.bio_find = 0 

        if plug.bio_find == 0:
            clear_sell_bio_table = True   

    if clear_sell_bio_table:
        # tabela bio tmp utracone dane
        data_db.finish_sell_bio()
        if data_db.get_lost_bio_count() > 0:
            data_db.clear_lost_bio()
            data_db.export_bio_lost_sumary()

    config_trade_set()
    config_value_set()
    update_display("Sumary Organic {:,}".format(plug.exobiologist_Organic), True)


# saasignalsfound

def update_bio_saa(entry):     
    plug.exploration_L3scan += 1
    if "Signals" in entry:
        sig = entry["Signals"]
        for sg in sig:
            if "Type_Localised" in sg: 
                localised = sg['Type_Localised']               
                if localised == "Biological":
                    if not data_db.check_planet_biosaa(entry["BodyID"], entry["BodyName"], 
                                                       entry["SystemAddress"], sg["Count"]):   
                        plug.exobiologist_Planets += 1
    config_value_set()
    update_display()            


# fssbodysignals

def update_bio_fss(entry):                  
    if "Signals" in entry:
        sig = entry["Signals"]
        for sg in sig:
            if "Type_Localised" in sg:
                localised = sg['Type_Localised']
                if localised == "Biological":
                    data_db.check_planet_biofss(entry["BodyID"], entry["BodyName"],
                                                entry["SystemAddress"], sg["Count"])


def update_bio_sample(entry):
    if "ScanType" in entry:
        if entry["ScanType"] == "Analyse":
            timestamp = entry["timestamp"]   # "timestamp":"2024-05-28T08:00:00Z"
            timestamp = timestamp.replace("T", " ")
            timestamp = timestamp.replace("Z", "")
            system_id = entry["SystemAddress"]
            planet_id = entry["Body"]
            bio_codex = entry["Species"]
            bio_name = entry["Species_Localised"]
            bio_variant = entry["Variant_Localised"]
            bio_variant = bio_variant.replace(bio_name, "")
            bio_variant = bio_variant.replace(" - ", "")
            bio_cost = data_db.get_bio_cost(bio_codex)
            plug.exobiologist_Unique = data_db.get_bio_unique_count()
            data_db.set_bio(timestamp, system_id, data_db.name_system(system_id),
                            planet_id, data_db.name_planet(system_id, planet_id),
                            bio_name, bio_variant, bio_codex)
            data_db.set_sell_bio(timestamp, system_id, planet_id, bio_codex, bio_name, bio_variant, bio_cost)

            plug.bio_sell += bio_cost
            plug.bio_find += 1
            config_value_set()
            update_display()


def update_died(entry):
    if plug.bio_find > 0:     # data_db.get_sell_bio_count()
        timestamp = entry["timestamp"]   # "timestamp":"2024-05-28T08:00:00Z"
        timestamp = timestamp.replace("T", " ")
        timestamp = timestamp.replace("Z", "")
        time_event = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        data_db.export_bio_lost(time_event)
        data_db.finish_sell_bio()
        plug.bio_find = 0
        plug.bio_sell = 0
        config_value_set()
        update_display('Lost Bio Data - Export list to file', True)


def update_mining_refined():
    plug.miner_refined += 1
    config_value_set()
    update_display("Miner Refined {:,}".format(plug.miner_refined), True)


def update_docked(entry):
    if entry["StationType"] == "FleetCarrier":
        data_db.set_docked_fleet(entry["MarketID"])


def update_jump(entry):
    overlay_text = ""
    plug.curent_system = entry["SystemAddress"]
    plug.exploration_Jumps += 1
    jump_d = entry["JumpDist"]
    jump_c = math.floor(jump_d)
    jump_f = jump_d - jump_c
    plug.exploration_Distance += jump_c
    plug.exploration_Distance_f += jump_f    
    if plug.exploration_Distance_f > 1:
        jump_d = plug.exploration_Distance_f
        jump_c = math.floor(jump_d)
        plug.exploration_Distance += jump_c
        jump_f = jump_d - jump_c
        plug.exploration_Distance_f = jump_f
    overlay_text += "Jumps {:,} ".format(plug.exploration_Jumps)
    overlay_text += "Distance {:,}".format(plug.exploration_Distance)    

    # system  wizyted baza dany zapis  i sprawdzenie 
    if not data_db.check_system(plug.curent_system, entry["StarSystem"]):
        plug.exploration_Visited += 1
        overlay_text += "\n New System Visited {:,}".format(plug.exploration_Visited)

    config_value_set()
    update_display(overlay_text, True)


def update_mission_accepted(entry):
    if "PassengerCount" in entry:    
        data_db.set_mission(entry["MissionID"], entry["PassengerCount"], entry["PassengerVIPs"], entry["Reward"])


def update_mission_completed(entry):
    mission_id = entry["MissionID"]
    if data_db.find_id_mission(mission_id):
        passenger_count = data_db.get_passenger_count(mission_id)
        if data_db.get_vip(mission_id):
            plug.passengers_VIP += passenger_count
            overlay_text = "Passengers VIP {:,}".format(plug.passengers_VIP)  
        else:
            plug.passengers_Delivered += passenger_count
            overlay_text = "Passengers Delivered {:,}".format(plug.passengers_Delivered)  
        data_db.finish_mission(mission_id) 
        
        config_value_set()
        update_display(overlay_text, True)    


"""
"event":"SearchAndRescue", "MarketID":3228841728, 
                           "Name":"occupiedcryopod", 
                           "Name_Localised":"Occupied Escape Pod", 
                           "Count":2, 
                           "Reward":61326 }
"event":"SearchAndRescue", "MarketID":3224200192, 
                           "Name":"damagedescapepod", 
                           "Name_Localised":"Damaged Escape Pod", 
                           "Count":1, 
                           "Reward":16737 }
"event":"SearchAndRescue", "MarketID":3222042368, 
                           "Name":"thargoidpod", 
                           "Name_Localised":"Thargoid Bio-storage Capsule", 
                           "Count":5, 
                           "Reward":733235 }
"event":"SearchAndRescue", "MarketID":3221963776, 
                           "Name":"usscargoblackbox", "Name_Localised":"Black Box", "Count":1, "Reward":30974 }
"event":"SearchAndRescue", "MarketID":3221963776, 
                           "Name":"wreckagecomponents", 
                           "Name_Localised":"Wreckage Components", 
                           "Count":3, 
                           "Reward":26742 }


"""


def update_rescue(entry):
    timestamp = entry["timestamp"]   # "timestamp":"2024-05-28T08:00:00Z"
    timestamp = timestamp.replace("T", " ")
    timestamp = timestamp.replace("Z", "")
    pr_cr = entry["Reward"]
    market = entry["MarketID"]

    plug.rescue_Traded += entry["Count"]
    plug.trade_profit += pr_cr
    plug.trading_Markets += data_db.set_market(plug.curent_system, market, 'rescue')
    data_db.set_trade(timestamp, market, pr_cr)

    config_value_set()
    update_display("Rescue {:,}".format(plug.rescue_Traded), True)    


def update_statistics_tab(entry):
    if "Passengers" in entry:
        up_statistics = entry["Passengers"]
        plug.passengers_Delivered = up_statistics['Passengers_Missions_Delivered']
        plug.passengers_VIP = up_statistics['Passengers_Missions_VIP']

    if "Trading" in entry:
        up_statistics = entry["Trading"]
        plug.trading_Resources = up_statistics['Resources_Traded']
        plug.trading_Markets = up_statistics['Markets_Traded_With']

    if "Exploration" in entry:
        up_statistics = entry["Exploration"]
        plug.exploration_Distance = up_statistics['Total_Hyperspace_Distance']
        plug.exploration_Jumps = up_statistics['Total_Hyperspace_Jumps']
        plug.exploration_Visited = up_statistics['Systems_Visited']
        plug.exploration_L3scan = up_statistics['Planets_Scanned_To_Level_3']
        plug.explore_profit = up_statistics['Exploration_Profits']

    if "Search_And_Rescue" in entry:
        up_statistics = entry["Search_And_Rescue"]
        plug.rescue_Traded = up_statistics['SearchRescue_Traded']
        plug.rescue_FireOut = up_statistics['Settlements_State_FireOut']
        plug.rescue_Reboot = up_statistics['Settlements_State_Reboot']

    if "Mining" in entry:
        up_statistics = entry["Mining"]
        plug.miner_refined = up_statistics['Quantity_Mined']
        plug.miner_profit = up_statistics['Mining_Profits']

    if "Exobiology" in entry:
        up_statistics = entry["Exobiology"]
        plug.bio_profit = up_statistics['Organic_Data_Profits']
        plug.exobiologist_Organic = up_statistics['Organic_Data']
        plug.exobiologist_Planets = up_statistics['Organic_Planets']
        plug.exobiologist_Unique = up_statistics['Organic_Species_Encountered']

    if "Combat" in entry:
        up_statistics = entry["Combat"]

        plug.hunting_bonds = up_statistics['Bounties_Claimed']
        plug.hunting_bonds_profit = up_statistics['Bounty_Hunting_Profit']

        plug.combat_bonds = up_statistics['Combat_Bonds']
        plug.combat_profit = up_statistics['Combat_Bond_Profits']

        plug.soldier_bonds = up_statistics['OnFoot_Combat_Bonds']
        plug.soldier_profit = up_statistics['OnFoot_Combat_Bonds_Profits']

        plug.soldier_Total_Wins = up_statistics['ConflictZone_Total_Wins']
        plug.soldier_High_Wins = up_statistics['ConflictZone_High_Wins']
        settlement_d = up_statistics['Settlement_Defended']
        settlement_a = up_statistics['Settlement_Conquered']
        plug.soldier_Settlement = settlement_a + settlement_d

    if "TG_ENCOUNTERS" in entry:
        up_statistics = entry["TG_ENCOUNTERS"]
        kill = up_statistics['TG_ENCOUNTER_KILLED']
        if kill > plug.thargoid_kill:
            plug.thargoid_kill = up_statistics['TG_ENCOUNTER_KILLED']

    config_value_set()
    config_trade_set()
    update_display()

    #  LOG.log(f"update_statistics_tab {self.bio_profit}", "INFO"


def parse_config() -> None:
    plug.show_rank = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_rank', default=True))
    plug.show_combat_stats = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_combat_stats', default=True))
    plug.show_trade_stats = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_trade_stats', default=True))
    plug.show_v_stats = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_v_stats', default=True))

    plug.show_Traveller = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_Traveller', default=True))
    plug.show_Explorer = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_Explorer', default=True))
    plug.show_Trader = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_Trader', default=True))
    plug.show_Captain = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_Captain', default=True))

    plug.show_exobiologist_progress = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_exobiologist_progress', default=True))
    plug.show_mercenary_progress = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_mercenary_progress', default=True))
    plug.show_samaritan_progress = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_samaritan_progress', default=True))
    plug.show_miner_progress = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_miner_progress', default=True))            
    plug.show_dh_progress = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_dh_progress', default=True))

    plug.show_thargoid_progress = tk.BooleanVar(value=config.get_bool(key='InaraProgress_show_thargoid', default=True))

    plug.use_overlay = tk.BooleanVar(value=config.get_bool(key='InaraProgress_overlay', default=False))
    plug.overlay_color = tk.StringVar(value=config.get_str(key='InaraProgress_overlay_color', default='#ff0000'))
    plug.overlay_anchor_x = tk.IntVar(value=config.get_int(key='InaraProgress_overlay_anchor_x', default=1040))
    plug.overlay_anchor_y = tk.IntVar(value=config.get_int(key='InaraProgress_overlay_anchor_y', default=0))
    plug.overlay_info_x = tk.IntVar(value=config.get_int(key='InaraProgress_overlay_info_x', default=500))
    plug.overlay_info_y = tk.IntVar(value=config.get_int(key='InaraProgress_overlay_info_y', default=160))    

    plug.clear_data_db = tk.BooleanVar(value=config.get_bool(key='InaraProgress_clear_data_db', default=False))


def parse_config_value() -> None:
    # settings
    plug.combat_rank = data_db.get_setting('InaraProgress_combat_rank')
    plug.trade_rank = data_db.get_setting('InaraProgress_trade_rank')
    plug.explore_rank = data_db.get_setting('InaraProgress_explore_rank')
    plug.soldier_rank = data_db.get_setting('InaraProgress_soldier_rank')
    plug.exobiologist_rank = data_db.get_setting('InaraProgress_exobiologist_rank')
    plug.cqc_rank = data_db.get_setting('InaraProgress_cqc_rank')
    plug.empire_rank = data_db.get_setting('InaraProgress_empire_rank')
    plug.federation_rank = data_db.get_setting('InaraProgress_federation_rank')

    plug.combat = data_db.get_setting('InaraProgress_combat')
    plug.trade = data_db.get_setting('InaraProgress_trade')
    plug.explore = data_db.get_setting('InaraProgress_explore')
    plug.soldier = data_db.get_setting('InaraProgress_soldier')
    plug.exobiologist = data_db.get_setting('InaraProgress_exobiologist')
    plug.cqc = data_db.get_setting('InaraProgress_cqc')
    plug.empire = data_db.get_setting('InaraProgress_empire')
    plug.federation = data_db.get_setting('InaraProgress_federation')

    plug.hunting_bonds = data_db.get_setting('InaraProgress_hunting_bonds')
    plug.hunting_bonds_profit = data_db.get_setting('InaraProgress_hunting_bonds_profit')
    plug.hunting_bonds_tosell = data_db.get_setting('InaraProgress_hunting_bonds_tosell')
    plug.hunting_kill = data_db.get_setting('InaraProgress_hunting_kill')

    plug.combat_bonds = data_db.get_setting('InaraProgress_combat_bonds')
    plug.combat_profit = data_db.get_setting('InaraProgress_combat_profit')
    plug.combat_last_sum = data_db.get_setting('InaraProgress_combat_last_sum')
    plug.kill_bonds = data_db.get_setting('InaraProgress_kill_bonds')
    plug.kill_bonds_foot = data_db.get_setting('InaraProgress_kill_bonds_foot')
    plug.soldier_bonds = data_db.get_setting('InaraProgress_soldier_bonds')
    plug.soldier_profit = data_db.get_setting('InaraProgress_soldier_profit')
    plug.soldier_last_sum = data_db.get_setting('InaraProgress_soldier_last_sum')
    plug.soldier_Total_Wins = data_db.get_setting('InaraProgress_soldier_Total_Wins')
    plug.soldier_High_Wins = data_db.get_setting('InaraProgress_soldier_High_Wins')
    plug.soldier_Settlement = data_db.get_setting('InaraProgress_soldier_colonyDC')
    plug.exobiologist_Organic = data_db.get_setting('InaraProgress_exobiologist_Organic')
    plug.exobiologist_Planets = data_db.get_setting('InaraProgress_exobiologist_Planets')
    plug.exobiologist_Unique = data_db.get_setting('InaraProgress_exobiologist_Unique')
    plug.rescue_Traded = data_db.get_setting('InaraProgress_Rescue_Traded')
    plug.rescue_FireOut = data_db.get_setting('InaraProgress_Rescue_FireOut')
    plug.rescue_Reboot = data_db.get_setting('InaraProgress_Rescue_Reboot')
    plug.exploration_Distance = data_db.get_setting('InaraProgress_exploration_Distance')

    plug.exploration_Distance_f = data_db.get_setting('InaraProgress_exploration_Distance_f')
    plug.exploration_Jumps = data_db.get_setting('InaraProgress_exploration_Jumps')
    plug.exploration_Visited = data_db.get_setting('InaraProgress_exploration_Visited')
    plug.exploration_L3scan = data_db.get_setting('InaraProgress_exploration_L3scan')
    plug.passengers_Delivered = data_db.get_setting('InaraProgress_passengers_Delivered')
    plug.passengers_VIP = data_db.get_setting('InaraProgress_passengers_VIP')
    plug.trading_Resources = data_db.get_setting('InaraProgress_trading_Resources')
    plug.trading_Markets = data_db.get_setting('InaraProgress_trading_Markets')
    plug.miner_refined = data_db.get_setting('InaraProgress_miner_refined')

    plug.thargoid_kill = data_db.get_setting('InaraProgress_thargoid_kill')
    plug.thargoid_cyclops = data_db.get_setting('InaraProgress_thargoid_cyclops')
    plug.thargoid_basilisk = data_db.get_setting('InaraProgress_thargoid_basilisk')
    plug.thargoid_medusa = data_db.get_setting('InaraProgress_thargoid_medusa')
    plug.thargoid_hydra = data_db.get_setting('InaraProgress_thargoid_hydra')
    plug.thargoid_scout = data_db.get_setting('InaraProgress_thargoid_scout')
    plug.thargoid_hunter = data_db.get_setting('InaraProgress_thargoid_hunter')

    plug.trade_profit = data_db.get_setting('InaraProgress_trade_profit')
    plug.explore_profit = data_db.get_setting('InaraProgress_explore_profit')
    plug.bio_profit = data_db.get_setting('InaraProgress_bio_profit')
    plug.bio_sell = data_db.get_setting('InaraProgress_bio_bonus')
    plug.bio_find = data_db.get_setting('InaraProgress_bio_find') 
    plug.miner_profit = data_db.get_setting('InaraProgress_miner_profit')

    plug.wyd_il = data_db.get_setting('InaraProgress_wyd_il')
    plug.curent_system = data_db.get_setting("InaraProgress_curent_system")


def config_rank_set() -> None:
    data_db.set_setting("InaraProgress_combat_rank", plug.combat_rank)
    data_db.set_setting("InaraProgress_trade_rank", plug.trade_rank)
    data_db.set_setting("InaraProgress_explore_rank", plug.explore_rank)
    data_db.set_setting("InaraProgress_soldier_rank", plug.soldier_rank)
    data_db.set_setting("InaraProgress_exobiologist_rank", plug.exobiologist_rank)
    data_db.set_setting("InaraProgress_cqc_rank", plug.cqc_rank)
    data_db.set_setting("InaraProgress_empire_rank", plug.empire_rank)
    data_db.set_setting("InaraProgress_federation_rank", plug.federation_rank)

    data_db.set_setting("InaraProgress_combat", plug.combat)
    data_db.set_setting("InaraProgress_trade", plug.trade)
    data_db.set_setting("InaraProgress_explore", plug.explore)
    data_db.set_setting("InaraProgress_soldier", plug.soldier)
    data_db.set_setting("InaraProgress_exobiologist", plug.exobiologist)
    data_db.set_setting("InaraProgress_cqc", plug.cqc)
    data_db.set_setting("InaraProgress_empire", plug.empire)
    data_db.set_setting("InaraProgress_federation", plug.federation)    


def config_value_set() -> None:
    data_db.set_setting("InaraProgress_hunting_bonds", plug.hunting_bonds)
    data_db.set_setting('InaraProgress_hunting_bonds_tosell', plug.hunting_bonds_tosell)
    data_db.set_setting("InaraProgress_hunting_bonds_profit", plug.hunting_bonds_profit)
    data_db.set_setting('InaraProgress_hunting_kill', plug.hunting_kill)

    data_db.set_setting("InaraProgress_combat_bonds", plug.combat_bonds)
    data_db.set_setting("InaraProgress_combat_profit", plug.combat_profit)
    data_db.set_setting("InaraProgress_combat_last_sum", plug.combat_last_sum)
    data_db.set_setting("InaraProgress_soldier_bonds", plug.soldier_bonds)
    data_db.set_setting("InaraProgress_soldier_profit", plug.soldier_profit)
    data_db.set_setting("InaraProgress_soldier_last_sum", plug.soldier_last_sum)
    data_db.set_setting("InaraProgress_kill_bonds", plug.kill_bonds)
    data_db.set_setting("InaraProgress_kill_bonds_foot", plug.kill_bonds_foot)
    data_db.set_setting("InaraProgress_soldier_Total_Wins", plug.soldier_Total_Wins)
    data_db.set_setting("InaraProgress_soldier_High_Wins", plug.soldier_High_Wins)
    data_db.set_setting("InaraProgress_soldier_colonyDC", plug.soldier_Settlement)
    data_db.set_setting("InaraProgress_exobiologist_Organic", plug.exobiologist_Organic)
    data_db.set_setting("InaraProgress_exobiologist_Planets", plug.exobiologist_Planets)
    data_db.set_setting("InaraProgress_exobiologist_Unique", plug.exobiologist_Unique)
    data_db.set_setting('InaraProgress_Rescue_Traded', plug.rescue_Traded)
    data_db.set_setting('InaraProgress_Rescue_FireOut', plug.rescue_FireOut)
    data_db.set_setting('InaraProgress_Rescue_Reboot', plug.rescue_Reboot)
    data_db.set_setting('InaraProgress_exploration_Distance', plug.exploration_Distance)
    data_db.set_setting_f('InaraProgress_exploration_Distance_f', plug.exploration_Distance_f)
    data_db.set_setting('InaraProgress_exploration_Jumps', plug.exploration_Jumps)
    data_db.set_setting('InaraProgress_exploration_Visited', plug.exploration_Visited)
    data_db.set_setting('InaraProgress_exploration_L3scan', plug.exploration_L3scan)
    data_db.set_setting('InaraProgress_passengers_Delivered', plug.passengers_Delivered)
    data_db.set_setting('InaraProgress_passengers_VIP', plug.passengers_VIP)
    data_db.set_setting('InaraProgress_trading_Resources', plug.trading_Resources)
    data_db.set_setting('InaraProgress_trading_Markets', plug.trading_Markets)
    data_db.set_setting('InaraProgress_miner_refined', plug.miner_refined)

    data_db.set_setting('InaraProgress_thargoid_kill', plug.thargoid_kill)
    data_db.set_setting('InaraProgress_thargoid_cyclops', plug.thargoid_cyclops)
    data_db.set_setting('InaraProgress_thargoid_basilisk', plug.thargoid_basilisk)
    data_db.set_setting('InaraProgress_thargoid_medusa', plug.thargoid_medusa)
    data_db.set_setting('InaraProgress_thargoid_hydra', plug.thargoid_hydra)
    data_db.set_setting('InaraProgress_thargoid_scout', plug.thargoid_scout)
    data_db.set_setting('InaraProgress_thargoid_hunter', plug.thargoid_hunter)

    data_db.set_setting("InaraProgress_bio_bonus", plug.bio_sell)
    data_db.set_setting("InaraProgress_bio_find", plug.bio_find)
    data_db.set_setting("InaraProgress_curent_system", plug.curent_system)


def config_trade_set() -> None:
    data_db.set_setting("InaraProgress_bio_profit", plug.bio_profit)

    data_db.set_setting("InaraProgress_explore_profit", plug.explore_profit)
    data_db.set_setting("InaraProgress_trade_profit", plug.trade_profit)
    data_db.set_setting("InaraProgress_miner_profit", plug.miner_profit)


def config_wyd_set() -> None:
    data_db.set_setting("InaraProgress_wyd_il", plug.wyd_il)


def journals_parse():
    # plug.button.config(text='Wait Parsing')
    LOG.log('Wait Parsing', 'INFO')
    config_value_set()
    plug.button.config(text='Parsing Done')

    parse_journals(plug.clear_data_db.get())
    parse_config_value()
    update_display()
    LOG.log('Parsing Done', 'INFO')


def clear_bio_counter():
    plug.bio_find = 0
    plug.bio_sell = 0


def plugin_start3(plugin_dir: str) -> str:

    data_db.init()
    plug.sql_session = Session(data_db.get_engine())

    return plug.NAME


def plugin_stop() -> None:
    if plug.overlay.available():
        plug.overlay.disconnect()    
    #  Save our prefs
    config_value_set()
    config_trade_set()
    config_rank_set()
    data_db.shutdown()


def plugin_prefs(parent: Nb.Frame, cmdr: str, is_beta: bool) -> Nb.Frame:
    color_button = None

    def color_chooser() -> None:
        (_, color) = tkColorChooser.askcolor(
            plug.overlay_color.get(), title='Overlay Color', parent=plug.parent
        )

        if color:
            plug.overlay_color.set(color)
            if color_button is not None:
                color_button['foreground'] = color

    x_padding = 10
    x_button_padding = 12    
    y_padding = 2
    frame = Nb.Frame(parent)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=1)

    HyperlinkLabel(frame, text=const.plugin_name, background=Nb.Label().cget('background'),
                   url='https://github.com/mauxion2/InaraProgress/releases', underline=True) \
        .grid(row=1, padx=x_padding, sticky=tk.W)
    Nb.Label(frame, text='Version %s' % const.plugin_version).grid(row=1, column=2, padx=x_padding, sticky=tk.E)

    ttk.Separator(frame).grid(row=5, columnspan=3, pady=y_padding * 2, sticky=tk.EW)

    Nb.Checkbutton(
        frame,
        text='Show Ranks',
        variable=plug.show_rank,
    ).grid(row=8, column=0, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Combat Progress', variable=plug.show_combat_stats,
    ).grid(row=9, column=0, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Thargoid Progress', variable=plug.show_thargoid_progress,
    ).grid(row=10, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Trade Profit', variable=plug.show_trade_stats,
    ).grid(row=11, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Vertical', variable=plug.show_v_stats,
    ).grid(row=12, padx=12, pady=(5, 0), sticky=tk.W) 

    # colum 2
    Nb.Checkbutton(
        frame, text='Show Exobiologist Progress', variable=plug.show_exobiologist_progress,
    ).grid(row=8, column=1, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Mercenary Progress', variable=plug.show_mercenary_progress,
    ).grid(row=9, column=1, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Samaritan Progress', variable=plug.show_samaritan_progress,
    ).grid(row=10, column=1, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Miner Progress', variable=plug.show_miner_progress,
    ).grid(row=11, column=1, padx=12, pady=(5, 0), sticky=tk.W)
    Nb.Checkbutton(
        frame, text='Show Decorated Hero', variable=plug.show_dh_progress,
    ).grid(row=12, column=1, padx=12, pady=(5, 0), sticky=tk.W) 

    # colum 3
    Nb.Checkbutton(
        frame, text='Show Traveller', variable=plug.show_Traveller,
    ).grid(row=8, column=2, padx=12, pady=(5, 0), sticky=tk.W) 
    Nb.Checkbutton(
        frame, text='Show Explorer', variable=plug.show_Explorer,
    ).grid(row=9, column=2, padx=12, pady=(5, 0), sticky=tk.W) 
    Nb.Checkbutton(
        frame, text='Show Trader', variable=plug.show_Trader,
    ).grid(row=10, column=2, padx=12, pady=(5, 0), sticky=tk.W) 
    Nb.Checkbutton(
        frame, text='Show Captain', variable=plug.show_Captain,
    ).grid(row=11, column=2, padx=12, pady=(5, 0), sticky=tk.W) 

    vcmd = (frame.register(validate_int))
    # Overlay settings
    ttk.Separator(frame).grid(row=15, columnspan=3, pady=y_padding * 2, sticky=tk.EW)

    Nb.Label(frame,
             text='EDMC Overlay Integration',
             justify=tk.LEFT) \
        .grid(row=20, column=0, padx=x_padding, sticky=tk.NW)
    Nb.Checkbutton(
        frame,
        text='Enable overlay',
        variable=plug.use_overlay
    ).grid(row=21, column=0, padx=x_button_padding, pady=0, sticky=tk.W)
    color_button = tk.Button(frame, text='Text Color', foreground=plug.overlay_color.get(),
                             background='grey4', command=lambda: color_chooser()
                             )
    color_button.grid(row=21, column=1, padx=x_button_padding, pady=y_padding, sticky=tk.W)

    anchor_frame = Nb.Frame(frame)
    anchor_frame.grid(row=21, column=2, sticky=tk.NSEW)
    anchor_frame.columnconfigure(4, weight=1)

    Nb.Label(anchor_frame, text='Display Positon:') \
        .grid(row=0, column=0, sticky=tk.W)
    Nb.Label(anchor_frame, text='X') \
        .grid(row=0, column=1, sticky=tk.W)
    Nb.EntryMenu(
        anchor_frame, text=plug.overlay_anchor_x.get(), textvariable=plug.overlay_anchor_x,
        width=8, validate='all', validatecommand=(vcmd, '%P')
    ).grid(row=0, column=2, sticky=tk.W)
    Nb.Label(anchor_frame, text='Y') \
        .grid(row=0, column=3, sticky=tk.W)
    Nb.EntryMenu(
        anchor_frame, text=plug.overlay_anchor_y.get(), textvariable=plug.overlay_anchor_y,
        width=8, validate='all', validatecommand=(vcmd, '%P')
    ).grid(row=0, column=4, sticky=tk.W)

    Nb.Label(anchor_frame, text='Info Positon:') \
        .grid(row=1, column=0, sticky=tk.W)
    Nb.Label(anchor_frame, text='X') \
        .grid(row=1, column=1, sticky=tk.W)
    Nb.EntryMenu(
        anchor_frame, text=plug.overlay_info_x.get(), textvariable=plug.overlay_info_x,
        width=8, validate='all', validatecommand=(vcmd, '%P')
    ).grid(row=1, column=2, sticky=tk.W)
    Nb.Label(anchor_frame, text='Y') \
        .grid(row=1, column=3, sticky=tk.W)
    Nb.EntryMenu(
        anchor_frame, text=plug.overlay_info_y.get(), textvariable=plug.overlay_info_y,
        width=8, validate='all', validatecommand=(vcmd, '%P')
    ).grid(row=1, column=4, sticky=tk.W)

    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=55, columnspan=3, pady=y_padding * 2, sticky=tk.EW)

    plug.button = Nb.Button(frame, text='Journal Parsing', command=journals_parse)
    plug.button.grid(row=60, column=0, padx=x_padding, sticky=tk.SW)

    plug.clear_data_db.set(False)

    Nb.Checkbutton(
        frame,
        text='All Log Parsing',
        variable=plug.clear_data_db
    ).grid(row=60, column=1, padx=x_button_padding, pady=0, sticky=tk.W)

    button = Nb.Button(frame, text='Clear Bio Counter', command=clear_bio_counter)
    button.grid(row=65, column=0, padx=x_padding, sticky=tk.SW)


    return frame


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    config.set('InaraProgress_show_rank', plug.show_rank.get())
    config.set('InaraProgress_show_trade_stats', plug.show_trade_stats.get())
    config.set('InaraProgress_show_combat_stats', plug.show_combat_stats.get())
    config.set('InaraProgress_show_v_stats', plug.show_v_stats.get())

    config.set('InaraProgress_show_Traveller', plug.show_Traveller.get())
    config.set('InaraProgress_show_Explorer', plug.show_Explorer.get())
    config.set('InaraProgress_show_Trader', plug.show_Trader.get())
    config.set('InaraProgress_show_Captain', plug.show_Captain.get())    

    config.set('InaraProgress_show_exobiologist_progress', plug.show_exobiologist_progress.get())
    config.set('InaraProgress_show_mercenary_progress', plug.show_mercenary_progress.get())
    config.set('InaraProgress_show_samaritan_progress', plug.show_samaritan_progress.get())
    config.set('InaraProgress_show_miner_progress', plug.show_miner_progress.get()) 
    config.set('InaraProgress_show_dh_progress', plug.show_dh_progress.get())   

    config.set('InaraProgress_show_thargoid', plug.show_thargoid_progress.get())

    config.set('InaraProgress_overlay', plug.use_overlay.get())
    config.set('InaraProgress_overlay_color', plug.overlay_color.get())
    config.set('InaraProgress_overlay_anchor_x', plug.overlay_anchor_x.get())
    config.set('InaraProgress_overlay_anchor_y', plug.overlay_anchor_y.get())
    config.set('InaraProgress_overlay_info_x', plug.overlay_info_x.get())
    config.set('InaraProgress_overlay_info_y', plug.overlay_info_y.get())    

    # config.set('InaraProgress_clear_data_db', plug.clear_data_db.get())

    setup_frame_new()
    update_stats()
    update_display('Test Display Positon Info', True)


def version_check() -> str:
    """
    Parse latest GitHub release version

    :return: The latest version string if it's newer than ours
    """

    try:
        req = requests.get(url='https://api.github.com/repos/mauxion2/InaraProgress/releases/latest')
        data = req.json()
        if req.status_code != requests.codes.ok:
            raise requests.RequestException
    except (requests.RequestException, requests.JSONDecodeError):
        LOG.log('Failed to parse GitHub release info', "INFO")
        return ''

    version = semantic_version.Version(data['tag_name'][1:])
    if version > plug.VERSION:
        return str(version)
    return ''


def validate_int(val: str) -> bool:
    if val.isdigit() or val == "":
        return True
    return False


def plugin_app(parent: tk.Frame) -> tk.Frame:
    parse_config()
    parse_config_value()
    plug.parent = parent
    if len(plug.labels) == 0:  # Initialize the UI   
        plug.frame = tk.Frame(parent)
        setup_frame_new()
        update_stats()
        update_display()
        update = version_check()
        if update != '':
            update_frame = tk.Frame(plug.frame, borderwidth=1, relief="groove")
            update_frame.columnconfigure(0, weight=1, uniform="r")
            update_frame.columnconfigure(1, weight=1, uniform="r")
            update_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW)
            inara_label = tk.Label(update_frame, text="InaraProgress")
            inara_label.grid(row=0, column=0)
            text = f'Version {update} is now available'
            url = f'https://github.com/mauxion2/InaraProgress/releases/tag/v{update}'
            plug.update_button = HyperlinkLabel(update_frame, text=text, url=url)
            plug.update_button.grid(row=0, column=1)       
    theme.update(plug.frame)
    return plug.frame


def dashboard_entry(cmdr: str, is_beta: bool, entry: dict[str, any]) -> str:
    # status = StatusFlags(entry['Flags'])
    status2 = StatusFlags2(0)
    if 'Flags2' in entry:
        status2 = StatusFlags2(entry['Flags2'])
    update = False

    # test onfoot  combat on foot  ON_FOOT   PLANET_ON_FOOT   EXTERIOR_ON_FOOT

    if StatusFlags2.PLANET_ON_FOOT in status2:
        if StatusFlags2.HANGAR_ON_FOOT in status2:
            on_foot = False
        else:
            on_foot = True
    else:
        on_foot = False

    if plug.On_Foot != on_foot:
        plug.On_Foot = on_foot
        update = True

    if update:
        update_display()

    return ''


def journal_entry(cmdr: str, is_beta: bool, system: str,
                  station: str, entry: MutableMapping[str, Any], state: Mapping[str, Any]):
    match entry['event']:
        case 'Statistics':
            # LOG.log(f"Event Statistics", "INFO")
            update_statistics_tab(entry)
        case 'Progress':
            update_progress(entry)
        case 'Rank':
            update_ranks(entry)
        case 'Promotion':
            update_promotion(entry)
        case 'Bounty':
            update_hunter_bounty(entry)
        case 'RedeemVoucher':
            update_redeem_voucher(entry)
        case 'FactionKillBond':
            update_combat_bond(entry)
        case 'MarketBuy':
            update_market(entry, True)
        case 'MarketSell':
            update_market(entry, False)
        case 'SellExplorationData':
            update_exp_data(entry)
        case 'MultiSellExplorationData':
            update_exp_data(entry)
        case 'SellOrganicData':
            # LOG.log(f"Event SellOrganicData", "INFO")
            update_bio_data(entry)
        case 'SAASignalsFound':
            update_bio_saa(entry)
        case 'FSSBodySignals':
            update_bio_fss(entry)
        case 'ScanOrganic':
            update_bio_sample(entry)
        case 'MiningRefined':
            update_mining_refined()
        case 'FSDJump':
            update_jump(entry)
        case 'SearchAndRescue':
            update_rescue(entry)
        case 'MissionAccepted':
            update_mission_accepted(entry)
        case 'MissionCompleted':
            update_mission_completed(entry)
        case 'Docked':
            update_docked(entry)
        case 'Died':
            update_died(entry)
