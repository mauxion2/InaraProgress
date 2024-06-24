plugin_name = 'InaraProgress'
plugin_version = '1.5.0'

combat_ranks = {0: "Harmless", 1: "Mostly Harmless", 2: "Novice", 3: "Competent", 4: "Expert",
                5: "Master", 6: "Dangerous", 7: "Deadly", 8: "Elite", 9: "Elite I", 10: "Elite II",
                11: "Elite III", 12: "Elite IV", 13: "Elite V"}

trade_ranks = {0: "Penniless", 1: "Mostly Penniless", 2: "Peddler", 3: "Dealer", 4: "Merchant",
               5: "Broker", 6: "Entrepreneur", 7: "Tycoon", 8: "Elite", 9: "Elite I", 10: "Elite II",
               11: "Elite III", 12: "Elite IV", 13: "Elite V"}

explore_ranks = {0: "Aimless", 1: "Mostly Aimless", 2: "Scout", 3: "Surveyor", 4: "Trailblazer",
                 5: "Pathfinder", 6: "Ranger", 7: "Pioneer", 8: "Elite", 9: "Elite I", 10: "Elite II",
                 11: "Elite III", 12: "Elite IV", 13: "Elite V"}

soldier_ranks = {0: "Defenceless", 1: "Mostly Defenceless", 2: "Rookie", 3: "Soldier", 4: "Gunslinger",
                 5: "Warrior", 6: "Gladiator", 7: "Deadeye", 8: "Elite", 9: "Elite I", 10: "Elite II",
                 11: "Elite III", 12: "Elite IV", 13: "Elite V"}

exobiologist_ranks = {0: "Directionless", 1: "Mostly Directionless", 2: "Compiler", 3: "Collector", 4: "Cataloguer",
                      5: "Taxonomist", 6: "Ecologist", 7: "Geneticist", 8: "Elite", 9: "Elite I", 10: "Elite II",
                      11: "Elite III", 12: "Elite IV", 13: "Elite V"}

cqc_ranks = {0: "Helpless", 1: "Mostly Helpless", 2: "Amateur", 3: "Semi Professional", 4: "Professional",
             5: "Champion", 6: "Hero", 7: "Legend", 8: "Elite", 9: "Elite I", 10: "Elite II",
             11: "Elite III", 12: "Elite IV", 13: "Elite V"}

federation_ranks = {0: "None", 1: "Recruit", 2: "Cadet", 3: "Midshipman", 4: "Petty Officer",
                    5: "Chief Petty Officer", 6: "Warrant Officer", 7: "Ensign", 8: "Lieutenant",
                    9: "Lieutenant Commander", 10: "Post Commander",
                    11: "Post Captain", 12: "Rear Admiral", 13: "Vice Admiral", 14: "Admiral"}

empire_ranks = {0: "None", 1: "Outsider", 2: "Serf", 3: "Master", 4: "Squire",
                5: "Knight", 6: "Lord", 7: "Baron", 8: "Viscount", 9: "Count", 10: "Earl",
                11: "Marquis", 12: "Duke", 13: "Prince", 14: "King"}


Traveller_Inara = {"Distance": {1: 25000, 2: 50000, 3: 100000, 4: 250000, 5: 500000},
                   "Jumps": {1: 0, 2: 1000, 3: 2500, 4: 5000, 5: 10000}}

Explorer_Inara = {"Visited": {1: 1000, 2: 2500, 3: 5000, 4: 7500, 5: 10000},
                  "L3scans": {1: 0, 2: 1000, 3: 5000, 4: 10000, 5: 20000}}

Exobiologist_Inara = {"Organic": {1: 25, 2: 50, 3: 100, 4: 250, 5: 500},
                      "Planets": {1: 5, 2: 10, 3: 25, 4: 50, 5: 100},
                      "Unique": {1: 3, 2: 10, 3: 25, 4: 50, 5: 75}}

Soldier_Inara = {"Bonds": {1: 500, 2: 1000, 3: 2000, 4: 4000, 5: 7500}}

Hunter_Inara = {"Bonds": {1: 500, 2: 1000, 3: 2000, 4: 4000, 5: 7500}}

Mercenary_Inara = {"Swon": {1: 10, 2: 50, 3: 100, 4: 250, 5: 500},
                   "Hwon": {1: 0, 2: 10, 3: 50, 4: 100, 5: 250},
                   "settlements": {1: 0, 2: 0, 3: 5, 4: 10, 5: 25}}

Xeno_Inara = {"Killed": {1: 100, 2: 500, 3: 1000, 4: 2500, 5: 5000},
              "Interceptors": {1: 0, 2: 10, 3: 25, 4: 50, 5: 100},
              "Basilisk": {1: 0, 2: 0, 3: 10, 4: 25, 5: 50},
              "Medusa": {1: 0, 2: 0, 3: 0, 4: 10, 5: 25},
              "Hydra": {1: 0, 2: 0, 3: 0, 4: 0, 5: 10}}

Trader_Inara = {"Commodities":  {1: 1000, 2: 50000, 3: 100000, 4: 200000, 5: 400000},
                "Market": {1: 0, 2: 10, 3: 25, 4: 50, 5: 100}}

Miner_Inara = {"Refined": {1: 1000, 2: 2500, 3: 5000, 4: 10000, 5: 25000}}

Samaritan_Inara = {"Rescued": {1: 1000, 2: 5000, 3: 10000, 4: 25000, 5: 50000},
                   "Rebooted": {1: 0, 2: 5, 3: 10, 4: 25, 5: 50},
                   "Fires": {1: 0, 2: 50, 3: 100, 4: 250, 5: 500}}

Captain_Inara = {"Passengers": {1: 1000, 2: 5000, 3: 10000, 4: 25000, 5: 50000},
                 "VIPs": {1: 0, 2: 100, 3: 500, 4: 1000, 5: 1500}}

Hero_Inara = {"Tier_5": {1: 10, 2: 25, 3: 50, 4: 75, 5: 100}}