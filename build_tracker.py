import json, re, os
from datetime import datetime, timedelta

# ===== ACTIVE MEMBERS (current roster) =====
ACTIVE = {
    # Current 42-member roster (verified May 29, 2026 from ClashSpot)
    # Removed: Aldich, Dohtem, OOLIJ, Redstone Copper, atlas
    "gen","stage6yo","Slayer","Gr8Conqueror","wato","Americanpatriot","drybonez",
    "crimpo","SwiftyKinja","Big Steppa","rour","Jac","Cole","stage5yo","studkiller","arius67'",
    "DE1","Kizaru","MiniPekka","UNSTOPPABLE ADI","Ste","Pam from HR","Sumairu","Marrow",
    "⚡️LSWreckless⚡️","uhlisuh","SurgeGold","MR. ASURAN YT","SWAGMUFFIN90",
    "Pharah","Brandon","Loading…","Stevie Wonder","jj","DandyPickle","F16","Tretor",
    "rinz","das","seth","Halid #1"
}

# ===== PLAYER TH LEVELS (from ClashSpot, in ClashSpot display order) =====
# Order = ClashSpot trophy/league rank within each TH tier — used as default sort
PLAYER_TH = {
    "Slayer": 18,
    "gen": 17, "Gr8Conqueror": 17,
    "stage6yo": 16, "wato": 16, "drybonez": 16,
    "Americanpatriot": 15, "Big Steppa": 15, "SwiftyKinja": 15, "stage5yo": 15, "DE1": 15,
    "crimpo": 14, "Cole": 14, "studkiller": 14, "rour": 14, "MiniPekka": 14,
    "Kizaru": 14, "Jac": 14, "Halid #1": 14, "SurgeGold": 14, "Loading…": 14,
    "Sumairu": 14, "Pam from HR": 14, "louis": 14, "imnotstraight10": 14,
    "the beast": 14, "seth": 14,
    "arius67'": 13, "Marrow": 13, "⚡️LSWreckless⚡️": 13, "Ste": 13, "uhlisuh": 13,
    "SWAGMUFFIN90": 13, "Brandon": 13, "Pharah": 13, "UNSTOPPABLE ADI": 13,
    "MR. ASURAN YT": 13, "jj": 13, "DandyPickle": 13, "F16": 13,
    "Stevie Wonder": 12, "das": 12, "rinz": 12,
    "Tretor": 11,
}
# In-game order (tiebreaker within same TH — matches the order user sees in-game)
_CS_ORDER = [
    "Slayer",
    "gen","Gr8Conqueror",
    "stage6yo","wato","drybonez",
    "Americanpatriot","Big Steppa","SwiftyKinja","stage5yo","DE1",
    "crimpo","Cole","studkiller","rour","MiniPekka","Kizaru","Jac","Halid #1",
    "SurgeGold","Loading…","Sumairu","Pam from HR","louis","imnotstraight10","the beast","seth",
    "arius67'","Marrow","⚡️LSWreckless⚡️","Ste","uhlisuh","SWAGMUFFIN90","Brandon","Pharah",
    "UNSTOPPABLE ADI","MR. ASURAN YT","jj","DandyPickle","F16",
    "Stevie Wonder","das","rinz",
    "Tretor",
]
_CS_RANK = {name: i+1 for i, name in enumerate(_CS_ORDER)}

# ===== PLAYER TAGS (tag → display name, auto-updated by update_tracker.py) =====
PLAYER_TAGS = {
    # AUTO-UPDATED by update_tracker.py
    "#209J8J0RL": "Big Steppa",
    "#2J9GYQRYC": "Jac",
    "#8J2V8998": "DE1",
    "#8L9J0R2QJ": "SWAGMUFFIN90",
    "#8YJCVQL9L": "rour",
    "#90QCVGU8U": "Slayer",
    "#G0VGRUCC": "SwiftyKinja",
    "#GJ20RJ8RP": "arius67'",
    "#GJLRURGC2": "Cole",
    "#GQJUGLQRQ": "stage6yo",
    "#GRGGPPQ8J": "Pam from HR",
    "#GRRYCUJP8": "crimpo",
    "#GV80Y9L0Y": "studkiller",
    "#L8UC9G0U8": "wato",
    "#LC020U2Q": "drybonez",
    "#LGJ9RC9Y9": "Halid #1",
    "#PGLV2YQC": "Kizaru",
    "#PRCQVCCV2": "Brandon",
    "#Q9UJG0RJP": "Sumairu",
    "#QCUCLPPJV": "Gr8Conqueror",
    "#QGRPYC928": "⚡️LSWreckless⚡️",
    "#QL8CV0P0": "gen",
    "#QLLPQV8VJ": "uhlisuh",
    "#QLPQC0GQ0": "Loading…",
    "#QLYP90RPV": "Ste",
    "#QP0CU0UC8": "stage5yo",
    "#R00L0CY9C": "MiniPekka",
    "#RQCJR8JV": "SurgeGold",
    "#XXXXXXXX": "DisplayName",
    "#Y0UUGPRRU": "Americanpatriot",
    "#YVCJC0VCQ": "Marrow",
}

# War end time (ISO 8601 UTC) — set by update_tracker.py when a war is active.
# JS uses this to display the smart-capture end time as "Next update" instead of next cron slot.
# Cleared by update_tracker.py when war ends or no war is active.
WAR_END_ISO = ""

# ===== RAW WAR DATA (newest first) =====
WAR_BLOCKS = [
("417523054","6/4/26","SS RAIDERS","30v30","""
#90QCVGU8U|Slayer|1|18|0|0|0|
#QL8CV0P0|gen|2|17|0|0|0|
#QCUCLPPJV|Gr8Conqueror|3|17|0|0|0|
#GQJUGLQRQ|stage6yo|4|16|0|0|0|
#L8UC9G0U8|wato|5|16|0|0|0|
#LC020U2Q|drybonez|6|16|0|0|0|
#209J8J0RL|Big Steppa|7|15|0|0|0|
#QP0CU0UC8|stage5yo|8|15|0|0|0|
#Y0UUGPRRU|Americanpatriot|9|15|0|0|0|
#G0VGRUCC|SwiftyKinja|10|15|0|0|0|
#8J2V8998|DE1|11|15|0|0|0|
#2J9GYQRYC|Jac|12|14|0|0|0|
#8YJCVQL9L|rour|15|14|0|0|0|
#GV80Y9L0Y|studkiller|17|14|0|0|0|
#RQCJR8JV|SurgeGold|18|14|0|0|0|
#Q9UJG0RJP|Sumairu|19|14|0|0|0|
#GRRYCUJP8|crimpo|20|14|0|0|0|
#R00L0CY9C|MiniPekka|21|14|0|0|0|
#LGJ9RC9Y9|Halid #1|22|14|0|0|0|
#GJLRURGC2|Cole|23|14|0|0|0|
#GRGGPPQ8J|Pam from HR|24|14|0|0|0|
#PGLV2YQC|Kizaru|25|14|0|0|0|
#QLPQC0GQ0|Loading…|26|14|0|0|0|
#GJ20RJ8RP|arius67'|28|13|0|0|0|
#PRCQVCCV2|Brandon|29|13|0|0|0|
#QGRPYC928|⚡️LSWreckless⚡️|30|13|0|0|0|
#QLYP90RPV|Ste|31|13|0|0|0|
#8L9J0R2QJ|SWAGMUFFIN90|33|13|0|0|0|
#YVCJC0VCQ|Marrow|34|13|0|0|0|
#QLLPQV8VJ|uhlisuh|35|13|0|0|0|
""", True, True),

("317373071","6/3/26","The Microwave","30v30","""
#90QCVGU8U|Slayer|1|18|0|0|0|
#QL8CV0P0|gen|2|17|1|3|3|2:3:3:16
#QCUCLPPJV|Gr8Conqueror|3|17|1|3|3|3:3:3:16
#GQJUGLQRQ|stage6yo|4|16|0|0|0|
#L8UC9G0U8|wato|5|16|1|2|2|5:2:2:16
#LC020U2Q|drybonez|6|16|0|0|0|
#209J8J0RL|Big Steppa|7|15|0|0|0|
#Y0UUGPRRU|Americanpatriot|8|15|0|0|0|
#QP0CU0UC8|stage5yo|9|15|0|0|0|
#G0VGRUCC|SwiftyKinja|10|15|1|2|2|12:2:2:16
#8J2V8998|DE1|11|15|1|2|2|13:2:2:16
#2J9GYQRYC|Jac|12|14|0|0|0|
#8YJCVQL9L|rour|15|14|0|0|0|
#GV80Y9L0Y|studkiller|17|14|1|2|2|16:2:2:15
#Q9UJG0RJP|Sumairu|18|14|1|2|2|20:2:2:15
#RQCJR8JV|SurgeGold|19|14|0|0|0|
#GRRYCUJP8|crimpo|20|14|0|0|0|
#R00L0CY9C|MiniPekka|21|14|1|3|3|23:3:3:15
#GRGGPPQ8J|Pam from HR|22|14|1|1|1|24:1:1:15
#GJLRURGC2|Cole|23|14|0|0|0|
#PGLV2YQC|Kizaru|24|14|0|0|0|
#LGJ9RC9Y9|Halid #1|25|14|0|0|0|
#QLPQC0GQ0|Loading…|26|14|0|0|0|
#GJ20RJ8RP|arius67'|28|13|0|0|0|
#PRCQVCCV2|Brandon|29|13|0|0|0|
#QGRPYC928|⚡️LSWreckless⚡️|31|13|0|0|0|
#8L9J0R2QJ|SWAGMUFFIN90|32|13|0|0|0|
#QLYP90RPV|Ste|33|13|0|0|0|
#YVCJC0VCQ|Marrow|34|13|0|0|0|
#QLLPQV8VJ|uhlisuh|35|13|1|2|2|43:2:2:13
""", True, True),

("217372345","6/2/26","Bama Boyz","30v30","""
#90QCVGU8U|Slayer|1|18|1|2|2|1:2:2:18
#QL8CV0P0|gen|2|17|1|3|3|2:3:3:18
#QCUCLPPJV|Gr8Conqueror|3|17|1|2|2|3:2:2:18
#GQJUGLQRQ|stage6yo|4|16|1|3|3|4:3:3:18
#L8UC9G0U8|wato|5|16|0|0|0|
#LC020U2Q|drybonez|6|16|1|1|1|6:1:1:17
#209J8J0RL|Big Steppa|7|15|1|1|1|7:1:1:17
#Y0UUGPRRU|Americanpatriot|8|15|1|2|2|8:2:2:17
#QP0CU0UC8|stage5yo|9|15|1|3|3|9:3:3:17
#G0VGRUCC|SwiftyKinja|10|15|1|2|2|11:2:2:16
#8J2V8998|DE1|11|15|1|1|1|12:1:1:16
#2J9GYQRYC|Jac|12|14|1|1|1|13:1:1:16
#8YJCVQL9L|rour|15|14|1|2|2|14:2:2:16
#Q9UJG0RJP|Sumairu|17|14|1|1|1|15:1:1:16
#RQCJR8JV|SurgeGold|18|14|1|2|2|16:2:2:16
#GV80Y9L0Y|studkiller|19|14|1|2|2|18:2:2:16
#GRRYCUJP8|crimpo|20|14|1|2|2|19:2:2:16
#R00L0CY9C|MiniPekka|21|14|1|2|2|20:2:2:17
#GJLRURGC2|Cole|22|14|1|2|2|21:2:2:16
#GRGGPPQ8J|Pam from HR|23|14|1|1|1|22:1:1:15
#PGLV2YQC|Kizaru|24|14|1|3|3|24:3:3:16
#LGJ9RC9Y9|Halid #1|25|14|1|3|3|25:3:3:16
#QLPQC0GQ0|Loading…|26|14|1|3|3|26:3:3:17
#PRCQVCCV2|Brandon|28|13|1|2|2|27:2:2:16
#GJ20RJ8RP|arius67'|29|13|1|3|3|28:3:3:16
#QGRPYC928|⚡️LSWreckless⚡️|31|13|1|2|2|30:2:2:16
#QLYP90RPV|Ste|32|13|1|3|3|31:3:3:14
#8L9J0R2QJ|SWAGMUFFIN90|33|13|1|3|3|32:3:3:16
#YVCJC0VCQ|Marrow|34|13|1|1|1|35:1:1:13
#QLLPQV8VJ|uhlisuh|35|13|1|3|3|36:3:3:11
""", False, True),

("273131437","5/29/26","Friendj of wer","30v30","""Slayer|1|2|6|1:3,2:3
Gr8Conqueror|2|2|5|1:3,4:2
stage6yo|3|2|6|3:3,2:3
wato|4|1|3|19:3
Big Steppa|5|2|6|5:3,4:3
Americanpatriot|6|0|0|
stage5yo|7|2|6|7:3,6:3
DE1|8|2|4|10:3,2:1
SwiftyKinja|9|2|6|9:3,8:3
Jac|10|2|6|9:3,20:3
crimpo|11|2|6|11:3,5:3
studkiller|12|2|6|12:3,16:3
MiniPekka|13|2|5|13:3,11:2
Cole|14|2|6|18:3,17:3
Kizaru|15|2|6|20:3,15:3
Pam from HR|16|1|2|16:2
Halid #1|17|1|3|17:3
Loading…|18|2|3|19:2,9:2
arius67'|19|2|6|14:3,19:3
MR. ASURAN YT|20|2|2|1:1,2:1
Ste|21|2|6|23:3,22:3
SWAGMUFFIN90|22|0|0|
uhlisuh|23|2|6|26:3,27:3
Marrow|24|2|6|21:3,26:3
jj|25|2|6|25:3,24:3
UNSTOPPABLE ADI|26|2|6|25:3,27:3
Stevie Wonder|27|2|2|5:1,9:2
das|28|2|6|28:3,27:3
rinz|29|2|6|29:3,30:3
Tretor|30|0|0|"""),

("272906647","5/27/26","⚡INDIAN KINGDOM","30v30","""Slayer|1|2|6|3:3,4:3
Gr8Conqueror|2|2|6|2:3,1:3
stage6yo|3|2|6|1:3,2:3
wato|4|1|3|22:3
Big Steppa|5|2|6|6:3,5:3
Americanpatriot|6|2|6|12:3,14:3
stage5yo|7|2|6|9:3,20:3
DE1|8|2|6|7:3,8:3
SwiftyKinja|9|2|5|9:2,10:3
Jac|10|2|4|15:2,14:2
crimpo|11|2|6|11:3,15:3
MiniPekka|12|2|4|12:2,14:2
studkiller|13|2|6|13:3,18:3
Cole|14|2|3|22:1,14:2
Mr.Minzy kipz|15|0|0|
Kizaru|16|2|6|16:3,21:3
Pam from HR|17|1|3|19:3
Halid #1|18|2|5|17:3,22:2
atlas|19|0|0|
Loading…|20|0|0|
Ste|21|2|5|25:3,22:2
SWAGMUFFIN90|22|2|2|1:1,2:1
uhlisuh|23|1|3|23:3
Marrow|24|2|5|24:3,22:2
jj|25|2|5|20:2,30:3
UNSTOPPABLE ADI|26|1|2|22:2
F16|27|1|3|26:3
Stevie Wonder|28|2|5|28:2,27:3
das|29|2|6|29:3,28:3
rinz|30|0|0|"""),

("272696863","5/25/26","SARYAGAW","35v35","""•KAILAN•|1|2|6|1:3,2:3
Onestatefan|2|0|0|
Slayer|3|2|4|3:2,2:2
gen|4|2|6|10:3,8:3
Gr8Conqueror|5|2|5|5:3,3:2
stage6yo|6|2|6|6:3,4:3
Big Steppa|7|2|6|12:3,16:3
Americanpatriot|8|2|6|7:3,11:3
stage5yo|9|2|6|9:3,13:3
DE1|10|2|4|12:2,3:2
SwiftyKinja|11|2|4|16:2,12:2
Jac|12|2|4|22:2,16:2
OOLIJ|13|0|0|
crimpo|14|2|6|11:3,9:3
Aldich|15|0|0|
SurgeGold|16|2|4|16:1,17:3
Cole|17|2|6|15:3,14:3
Pam from HR|18|2|4|18:3,16:1
Kizaru|19|2|5|19:3,16:2
studkiller|20|2|6|20:3,17:3
Loading…|21|2|6|21:3,25:3
MiniPekka|22|2|5|22:3,16:2
arius67'|23|2|3|16:2,4:1
Brandon|24|2|5|24:3,16:2
MR. ASURAN YT|25|0|0|
Ste|26|2|5|26:3,16:2
SWAGMUFFIN90|27|2|2|1:1,4:1
⚡️LSWreckless⚡️|28|1|3|28:3
uhlisuh|29|1|3|29:3
Marrow|30|2|5|16:2,23:3
UNSTOPPABLE ADI|31|1|3|31:3
jj|32|2|6|30:3,27:3
1234567890|33|0|0|
Stevie Wonder|34|2|6|34:3,33:3
das|35|2|6|35:3,32:3"""),

("272454773","5/23/26","UNITY ID","35v35","""Onestatefan|1|2|6|6:3,24:3
Slayer|2|2|5|7:3,1:2
gen|3|2|6|3:3,2:3
stage6yo|4|2|6|4:3,5:3
Big Steppa|5|2|6|8:3,9:3
Americanpatriot|6|2|4|1:2,2:2
stage5yo|7|2|6|6:3,5:3
DE1|8|2|4|3:2,4:2
Jac|9|2|6|28:3,35:3
OOLIJ|10|0|0|
crimpo|11|2|6|10:3,11:3
Pam from HR|12|2|6|29:3,34:3
Cole|13|2|6|13:3,12:3
Kizaru|14|2|6|19:3,32:3
studkiller|15|2|6|15:3,14:3
Loading…|16|2|4|16:1,20:3
``FNC legend``|17|0|0|
atlas|18|2|6|22:3,23:3
MiniPekka|19|2|6|18:3,17:3
kargho king|20|2|4|22:2,23:2
arius67'|21|2|6|21:3,16:3
MR. ASURAN YT|22|2|2|3:1,4:1
Brandon|23|2|3|23:2,28:1
Ste|24|2|6|30:3,24:3
SWAGMUFFIN90|25|2|3|1:1,2:2
gholey|26|0|0|
Marrow|27|2|5|27:3,19:2
UNSTOPPABLE ADI|28|0|0|
jj|29|2|6|25:3,26:3
ag 2|30|2|6|31:3,26:3
Stevie Wonder|31|0|0|
das|32|2|6|31:3,30:3
rinz|33|2|5|33:3,32:2
Tretor|34|2|2|1:2,2:0
high|35|0|0|"""),

("272138237","5/22/26","INVADERS","35v35","""Onestatefan|1|2|6|4:3,1:3
gen|2|1|3|5:3
stage6yo|3|2|6|3:3,27:3
Big Steppa|4|2|6|8:3,12:3
Americanpatriot|5|2|6|13:3,17:3
stage5yo|6|1|3|6:3
DE1|7|2|4|7:3,3:1
Jac|8|1|2|29:2
crimpo|9|2|5|9:3,13:2
Pam from HR|10|2|6|10:3,19:3
studkiller|11|2|6|11:3,14:3
Cole|12|2|5|20:2,25:3
Kizaru|13|2|4|13:1,23:3
``FNC legend``|14|0|0|
atlas|15|2|6|15:3,16:3
Loading…|16|1|2|15:2
MiniPekka|17|2|6|20:3,22:3
arius67'|18|2|5|18:3,20:2
kargho king|19|2|6|35:3,34:3
MR. ASURAN YT|20|0|0|
Ste|21|2|5|21:3,27:2
Brandon|22|2|4|22:2,25:2
SWAGMUFFIN90|23|2|4|29:3,1:1
gholey|24|2|4|29:2,22:2
uhlisuh|25|2|3|25:1,32:2
Marrow|26|2|6|26:3,24:3
UNSTOPPABLE ADI|27|2|5|28:3,23:2
jj|28|2|5|33:3,32:2
ag 2|29|2|4|30:3,29:1
Lalit|30|0|0|
Stevie Wonder|31|2|6|?:3,32:3
das|32|2|2|35:1,24:1
rinz|33|1|1|30:1
Tretor|34|2|3|29:2,4:1
high|35|1|1|34:1"""),

("271917758","5/20/26","Tyran","40v40","""Onestatefan|1|2|6|5:3,1:3
gen|2|2|6|3:3,4:3
stage6yo|3|2|6|2:3,6:3
Big Steppa|4|2|5|6:2,7:3
Americanpatriot|5|2|6|22:3,23:3
Jac|6|2|4|25:3,7:1
crimpo|7|2|6|12:3,21:3
stage5yo|8|2|6|9:3,8:3
DE1|9|2|6|14:3,10:3
Pam from HR|10|1|2|10:2
studkiller|11|2|6|11:3,13:3
SurgeGold|12|2|2|12:2,2:0
Cole|13|2|5|16:3,25:2
``FNC legend``|14|2|4|22:2,23:2
Loading…|15|2|4|15:2,14:2
atlas|16|2|6|19:3,18:3
Danish|17|0|0|
Aye|18|2|4|18:1,15:3
Kizaru|19|2|5|19:2,29:3
MiniPekka|20|2|6|20:3,17:3
ReuDan.TT|21|2|5|21:2,32:3
MR. ASURAN YT|22|2|6|28:3,30:3
kargho king|23|2|5|40:2,39:3
arius67'|24|2|5|25:2,27:3
Ste|25|2|6|36:3,34:3
Brandon|26|2|4|27:2,28:2
lokmane|27|0|0|
SWAGMUFFIN90|28|2|4|35:3,8:1
gholey|29|2|5|26:3,35:2
uhlisuh|30|2|5|30:2,39:3
Marrow|31|1|3|15:3
UNSTOPPABLE ADI|32|2|5|33:3,29:2
jj|33|2|4|32:1,37:3
ag 2|34|2|6|24:3,40:3
Lalit|35|0|0|
Stevie Wonder|36|1|2|40:2
das|37|2|5|39:2,38:3
rinz|38|0|0|
Tretor|39|2|2|8:1,12:1
high|40|2|3|40:2,39:1"""),

("271683120","5/18/26","Aikatsu likes","30v30","""Onestatefan|1|2|6|2:3,1:3
stage6yo|2|2|6|3:3,4:3
Big Steppa|3|2|5|5:3,2:2
Americanpatriot|4|2|5|23:3,2:2
stage5yo|5|2|4|8:3,1:1
crimpo|6|2|6|6:3,7:3
SurgeGold|7|2|4|21:3,2:1
Cole|8|1|2|23:2
Pam from HR|9|2|6|9:3,8:3
DE1|10|2|3|4:2,3:1
studkiller|11|1|3|10:3
Loading…|12|2|5|17:2,14:3
Aye|13|2|6|17:3,20:3
MiniPekka|14|2|5|17:2,18:3
arius67'|15|2|6|15:3,16:3
Ste|16|2|6|25:3,13:3
lokmane|17|0|0|
SWAGMUFFIN90|18|2|3|2:1,3:2
Brandon|19|2|5|19:3,18:2
gholey|20|2|6|30:3,22:3
⚡️LSWreckless⚡️|21|0|0|
Marrow|22|2|6|8:3,12:3
uhlisuh|23|2|4|23:1,24:3
DandyPickle|24|2|4|24:1,28:3
UNSTOPPABLE ADI|25|2|6|22:3,26:3
Stevie Wonder|26|0|0|
das|27|2|6|29:3,27:3
rinz|28|1|3|30:3
Tretor|29|2|2|4:1,2:1
high|30|0|0|"""),

("271426618","5/16/26","GEMBOX PATCH","30v30","""stage6yo|1|2|6|1:3,8:3
drybonez|2|2|3|8:1,3:2
Big Steppa|3|2|6|3:3,5:3
Americanpatriot|4|2|6|4:3,6:3
Sumairu|5|2|4|5:1,6:3
madmax|6|0|0|
crimpo|7|2|6|7:3,8:3
stage5yo|8|2|4|5:2,4:2
Cole|9|2|6|9:3,10:3
Pam from HR|10|2|6|11:3,17:3
DE1|11|2|6|18:3,6:3
studkiller|12|1|3|23:3
Aye|13|2|6|14:3,16:3
Kizaru|14|2|5|21:2,30:3
MiniPekka|15|2|6|15:3,13:3
MR. ASURAN YT|16|0|0|
arius67'|17|2|5|17:2,21:3
SWAGMUFFIN90|18|1|0|8:0
Brandon|19|2|3|19:1,26:2
⚡️LSWreckless⚡️|20|2|6|20:3,19:3
Marrow|21|2|4|21:1,22:3
uhlisuh|22|2|5|26:3,21:2
Pharah|23|2|5|21:2,25:3
DandyPickle|24|2|3|24:1,25:2
UNSTOPPABLE ADI|25|2|5|18:2,24:3
F16|26|1|2|26:2
Stevie Wonder|27|2|6|27:3,28:3
das|28|2|6|29:3,30:3
rinz|29|1|1|29:1
Tretor|30|1|1|6:1"""),

("271225938","5/14/26","12 DEC 2021","30v30","""stage6yo|1|2|6|1:3,3:3
drybonez|2|2|4|1:1,2:3
Big Steppa|3|2|6|4:3,3:3
Americanpatriot|4|2|6|12:3,7:3
Sumairu|5|2|6|5:3,6:3
madmax|6|2|6|11:3,18:3
stage5yo|7|2|3|1:1,3:2
crimpo|8|2|6|8:3,2:3
Cole|9|1|3|10:3
DE1|10|2|4|12:2,7:2
Pam from HR|11|1|2|7:2
studkiller|12|2|5|12:2,16:3
Aye|13|2|4|1:2,3:2
Kizaru|14|2|6|21:3,29:3
MiniPekka|15|2|6|15:3,13:3
MR. ASURAN YT|16|2|6|24:3,19:3
arius67'|17|2|5|7:2,17:3
SWAGMUFFIN90|18|2|1|5:1,4:0
Brandon|19|2|3|19:2,18:1
uhlisuh|20|2|5|26:3,24:2
Marrow|21|2|6|25:3,14:3
Pharah|22|2|5|22:3,21:2
⚡️LSWreckless⚡️|23|1|3|23:3
DandyPickle|24|2|4|24:2,21:2
UNSTOPPABLE ADI|25|2|6|27:3,20:3
F16|26|1|2|26:2
Stevie Wonder|27|2|4|24:2,19:2
das|28|2|5|28:3,12:2
Tretor|29|2|0|6:0,3:0
high|30|2|6|30:3,29:3"""),

("270965373","5/11/26","MiniMalizM","30v30","""stage6yo|1|2|6|1:3,2:3
Big Steppa|2|2|4|3:1,4:3
Americanpatriot|3|1|3|9:3
Sumairu|4|2|6|5:3,6:3
madmax|5|2|3|8:1,12:2
Cole|6|2|4|6:2,11:2
crimpo|7|2|6|7:3,18:3
DE1|8|2|6|8:3,16:3
studkiller|9|2|4|9:2,12:2
MALAYA|10|2|5|13:3,11:2
Loading…|11|2|4|12:2,15:2
Aye|12|2|5|12:3,16:2
MR. ASURAN YT|13|0|0|
MiniPekka|14|2|6|14:3,10:3
Lowkey09|15|0|0|
SWAGMUFFIN90|16|2|4|30:2,1:2
Brandon|17|2|4|17:3,16:1
Marrow|18|2|4|18:2,17:2
Pharah|19|1|3|27:3
uhlisuh|20|2|6|20:3,29:3
⚡️LSWreckless⚡️|21|2|6|21:3,22:3
DandyPickle|22|1|2|22:2
UNSTOPPABLE ADI|23|2|6|23:3,19:3
F16|24|2|6|24:3,28:3
Hey|25|0|0|
Stevie Wonder|26|2|6|26:3,25:3
MACK|27|0|0|
das|28|2|4|30:2,29:2
rinz|29|1|1|28:1
high|30|2|2|29:1,30:1"""),

("8Q0J0022Q","5/8/26","FarmLife26","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|3|2:3
Big Steppa|3|1|3|3:3
Americanpatriot|4|1|3|4:3
madmax|5|1|3|5:3
Cole|6|1|3|6:3
crimpo|7|1|3|17:3
DE1|8|1|2|8:2
Pam from HR|9|1|3|9:3
studkiller|10|1|3|10:3
MALAYA|11|1|3|11:3
Loading…|12|1|2|12:2
Aye|13|1|3|13:3
Kizaru|14|1|3|14:3
MR. ASURAN YT|15|1|3|15:3
MiniPekka|16|1|3|16:3
arius67'|17|1|3|7:3
SWAGMUFFIN90|18|1|3|18:3
Brandon|19|1|2|19:2
Marrow|20|1|3|20:3
Pharah|21|1|3|21:3
uhlisuh|22|1|3|22:3
⚡️LSWreckless⚡️|23|1|3|23:3
DandyPickle|24|1|1|24:1
UNSTOPPABLE ADI|25|1|3|25:3
F16|26|1|2|26:2
Stevie Wonder|27|1|3|27:3
das|28|1|1|28:1
rinz|29|1|1|29:1
high|30|1|2|30:2""", False, True),

("8Q0G02CGY","5/7/26","VSV WAR","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|3|2:3
Big Steppa|3|1|3|3:3
Americanpatriot|4|1|3|4:3
madmax|5|1|1|5:1
Cole|6|1|3|6:3
crimpo|7|1|3|7:3
DE1|8|1|2|8:2
Pam from HR|9|1|3|9:3
MALAYA|10|1|2|10:2
studkiller|11|1|3|11:3
Loading…|12|1|2|12:2
Aye|13|1|2|13:2
Kizaru|14|1|2|14:2
MR. ASURAN YT|15|1|3|15:3
MiniPekka|16|1|2|16:2
arius67'|17|1|2|17:2
SWAGMUFFIN90|18|1|3|18:3
Brandon|19|1|3|19:3
Marrow|20|1|3|20:3
uhlisuh|21|1|3|21:3
⚡️LSWreckless⚡️|22|1|3|22:3
DandyPickle|23|1|3|23:3
Pharah|24|1|3|24:3
UNSTOPPABLE ADI|25|1|3|25:3
F16|26|1|3|26:3
Stevie Wonder|27|0|0|
das|28|1|3|28:3
rinz|29|1|3|29:3
high|30|1|3|30:3""", False, True),

("8Q0L0VR82","5/6/26","SK¥ W@rriORS","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|2|2:2
Big Steppa|3|1|3|3:3
Americanpatriot|4|1|3|4:3
madmax|5|1|3|5:3
crimpo|6|1|3|6:3
DE1|7|1|3|7:3
Pam from HR|8|1|3|8:3
stage5yo|9|1|1|9:1
MALAYA|10|1|3|10:3
studkiller|11|1|3|11:3
Cole|12|1|3|12:3
Loading…|13|1|3|13:3
Aye|14|1|3|17:3
Kizaru|15|1|3|15:3
MR. ASURAN YT|16|1|3|16:3
arius67'|17|1|3|14:3
MiniPekka|18|1|3|18:3
Brandon|19|1|3|19:3
Marrow|20|1|3|20:3
uhlisuh|21|1|3|21:3
⚡️LSWreckless⚡️|22|1|2|22:2
DandyPickle|23|1|3|23:3
Pharah|24|1|3|24:3
UNSTOPPABLE ADI|25|1|3|25:3
F16|26|1|3|26:3
Stevie Wonder|27|1|3|27:3
das|28|1|3|28:3
rinz|29|1|3|29:3
high|30|1|3|30:3""", False, True),

("8Q0P0CYLR","5/5/26","UZB","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|3|2:3
Big Steppa|3|1|3|3:3
Americanpatriot|4|1|1|4:1
madmax|5|1|1|5:1
crimpo|6|1|3|6:3
Pam from HR|7|1|3|7:3
DE1|8|1|3|8:3
stage5yo|9|1|2|9:2
MALAYA|10|1|3|10:3
studkiller|11|1|3|11:3
Cole|12|1|3|12:3
Loading…|13|1|2|13:2
Aye|14|1|3|14:3
Kizaru|15|1|3|15:3
MR. ASURAN YT|16|1|3|16:3
MiniPekka|17|1|3|17:3
arius67'|18|1|3|18:3
Brandon|19|1|3|19:3
Marrow|20|1|3|20:3
⚡️LSWreckless⚡️|21|1|3|21:3
uhlisuh|22|1|3|22:3
DandyPickle|23|1|3|23:3
Pharah|24|1|3|24:3
UNSTOPPABLE ADI|25|1|3|25:3
F16|26|1|3|26:3
Stevie Wonder|27|1|3|27:3
das|28|1|3|28:3
rinz|29|1|3|29:3
high|30|1|3|30:3""", False, True),

("8Q0882R82","5/4/26","ClaSHonDeo","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|2|2:2
Big Steppa|3|1|3|3:3
Americanpatriot|4|1|3|4:3
madmax|5|1|3|5:3
crimpo|6|1|3|6:3
Pam from HR|7|1|3|7:3
DE1|8|1|3|8:3
MALAYA|9|1|3|9:3
studkiller|10|1|3|10:3
Cole|11|1|3|11:3
Loading…|12|1|3|12:3
Aye|13|1|3|13:3
Kizaru|14|1|3|14:3
MR. ASURAN YT|15|1|3|15:3
Lowkey09|16|0|0|
MiniPekka|17|1|3|17:3
arius67'|18|1|3|18:3
SWAGMUFFIN90|19|0|0|
Brandon|20|1|3|20:3
Marrow|21|1|3|21:3
uhlisuh|22|1|3|22:3
⚡️LSWreckless⚡️|23|1|3|23:3
DandyPickle|24|1|2|24:2
Pharah|25|1|3|25:3
UNSTOPPABLE ADI|26|1|3|26:3
Hey|27|0|0|
F16|28|1|3|28:3
Stevie Wonder|29|1|3|29:3
das|30|1|3|30:3""", False, True),

("8Q0020RCC","5/3/26","charaktala boys","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|2|2:2
Big Steppa|3|1|3|3:3
Americanpatriot|4|1|3|4:3
jk|5|1|3|5:3
madmax|6|1|3|6:3
Pam from HR|7|1|3|7:3
crimpo|8|1|3|8:3
DE1|9|1|2|9:2
stage5yo|10|1|2|10:2
MALAYA|11|1|2|11:2
Cole|12|1|3|12:3
studkiller|13|1|1|13:1
Loading…|14|1|3|14:3
Aye|15|1|3|15:3
Kizaru|16|1|3|16:3
MR. ASURAN YT|17|1|3|17:3
MiniPekka|18|1|3|18:3
arius67'|19|1|3|19:3
Marrow|20|1|3|20:3
uhlisuh|21|1|3|21:3
⚡️LSWreckless⚡️|22|1|3|22:3
DandyPickle|23|1|3|23:3
Pharah|24|1|3|24:3
UNSTOPPABLE ADI|25|1|3|25:3
F16|26|1|3|26:3
Stevie Wonder|27|1|3|27:3
MACK|28|0|0|
das|29|1|3|29:3
rinz|30|0|0|""", False, True),

("8LVUPY0R9","5/2/26","ViTALiTY","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|1|2:1
Big Steppa|3|1|3|3:3
Americanpatriot|4|1|3|4:3
jk|5|1|3|5:3
madmax|6|1|3|6:3
Pam from HR|7|1|3|7:3
crimpo|8|1|3|8:3
DE1|9|1|3|9:3
stage5yo|10|1|3|10:3
MALAYA|11|1|3|11:3
Cole|12|1|3|12:3
studkiller|13|1|3|13:3
Loading…|14|1|3|14:3
Aye|15|1|3|15:3
Kizaru|16|1|3|16:3
MR. ASURAN YT|17|1|3|17:3
MiniPekka|18|1|3|18:3
Lowkey09|19|1|3|19:3
arius67'|20|1|3|20:3
SWAGMUFFIN90|21|1|3|21:3
Brandon|22|1|3|22:3
Marrow|23|1|3|23:3
uhlisuh|24|1|3|24:3
DandyPickle|25|1|3|25:3
⚡️LSWreckless⚡️|26|1|3|26:3
UNSTOPPABLE ADI|27|1|3|27:3
Hey|28|1|3|28:3
F16|29|1|3|29:3
Stevie Wonder|30|1|3|30:3""", False, True),

("270475341","4/30/26","GOAT","30v30","""stage6yo|1|1|3|1:3
drybonez|2|2|6|4:3,5:3
Americanpatriot|3|2|6|7:3,20:3
JON JONES⁶⁶⁶TS®|4|2|6|2:3,3:3
⭐J⭐S⭐¹|5|2|5|6:3,1:2
Pam from HR|6|2|6|8:3,19:3
crimpo|7|2|6|11:3,9:3
DE1|8|2|4|4:2,5:2
stage5yo|9|0|0|
MALAYA|10|2|6|14:3,15:3
Cole|11|2|6|12:3,10:3
Blue NINJA|12|0|0|
studkiller|13|2|5|13:3,11:2
Aye|14|2|5|19:2,20:3
Kizaru|15|2|6|18:3,21:3
MR. ASURAN YT|16|0|0|
MiniPekka|17|2|6|17:3,15:3
arius67'|18|2|4|6:1,16:3
SWAGMUFFIN90|19|2|2|5:1,4:1
Brandon|20|1|2|21:2
Marrow|21|2|6|23:3,24:3
uhlisuh|22|2|4|22:3,20:1
DandyPickle|23|2|5|25:3,21:2
Jack|24|0|0|
UNSTOPPABLE ADI|25|2|6|26:3,17:3
Stevie Wonder|26|1|3|30:3
das|27|2|6|28:3,27:3
rinz|28|2|5|30:2,29:3
Tretor|29|2|6|20:3,19:3
high|30|2|6|30:3,29:3"""),

("270286010","4/28/26","Krasavchiki","30v30","""stage6yo|1|2|6|5:3,7:3
Americanpatriot|2|2|6|2:3,3:3
JON JONES⁶⁶⁶TS®|3|2|6|4:3,1:3
Pam from HR|4|2|6|20:3,27:3
crimpo|5|2|6|6:3,8:3
stage5yo|6|2|6|9:3,10:3
DE1|7|2|2|2:0,3:2
MALAYA|8|2|6|14:3,15:3
Cole|9|0|0|
Blue NINJA|10|2|1|2:0,3:1
Aye|11|2|4|4:3,5:1
studkiller|12|1|3|11:3
Kizaru|13|2|6|13:3,30:3
MR. ASURAN YT|14|2|2|2:1,1:1
Lowkey09|15|0|0|
MiniPekka|16|2|6|16:3,17:3
SWAGMUFFIN90|17|2|1|2:1,1:0
Brandon|18|2|5|18:3,20:2
Marrow|19|2|3|11:2,18:1
DandyPickle|20|2|5|20:2,24:3
⚡️LSWreckless⚡️|21|2|6|21:3,22:3
UNSTOPPABLE ADI|22|2|6|19:3,23:3
Jack|23|0|0|
Hey|24|0|0|
Stevie Wonder|25|2|6|25:3,26:3
pickledpigeon23|26|0|0|
das|27|2|6|29:3,28:3
rinz|28|1|3|30:3
Tretor|29|2|5|22:3,7:2
high|30|2|6|30:3,29:3"""),

("270045813","4/26/26","Bangladesh kin","35v35","""PsychoHaze16|1|0|0|
drybonez|2|2|5|4:3,2:2
Americanpatriot|3|2|4|3:2,1:2
Big Steppa|4|2|6|10:3,13:3
JON JONES⁶⁶⁶TS®|5|2|6|5:3,6:3
ridge|6|0|0|
Pam from HR|7|2|6|16:3,17:3
crimpo|8|2|6|8:3,7:3
DE1|9|2|6|9:3,31:3
MALAYA|10|2|6|11:3,12:3
Cole|11|2|6|20:3,21:3
Blue NINJA|12|2|5|18:2,23:3
Loading…|13|2|4|13:2,10:2
Aye|14|2|5|14:3,13:2
studkiller|15|2|5|15:3,14:2
Kizaru|16|2|6|30:3,22:3
Lowkey09|17|0|0|
MR. ASURAN YT|18|2|4|3:2,2:2
SWAGMUFFIN90|19|2|5|18:3,3:2
MiniPekka|20|2|5|20:2,19:3
Brandon|21|2|4|21:2,18:2
uhlisuh|22|2|4|22:1,32:3
Marrow|23|2|4|23:1,28:3
DandyPickle|24|2|4|23:2,29:2
UNSTOPPABLE ADI|25|2|6|25:3,26:3
⚡️LSWreckless⚡️|26|2|6|27:3,24:3
Jack|27|0|0|
Hey|28|0|0|
Stevie Wonder|29|2|5|29:3,23:2
pickledpigeon23|30|1|3|33:3
MACK|31|2|4|34:3,31:1
das|32|2|2|32:1,30:1
rinz|33|2|4|30:1,35:3
Tretor|34|2|3|20:1,22:2
high|35|2|2|32:1,31:1"""),

("269790839","4/24/26","البارون","35v35","""stage6yo|1|2|6|1:3,6:3
PsychoHaze16|2|2|6|2:3,5:3
drybonez|3|2|4|3:3,2:1
Americanpatriot|4|1|3|13:3
Big Steppa|5|2|3|1:1,3:2
Dragon|6|0|0|
ridge|7|0|0|
Pam from HR|8|2|6|24:3,16:3
stage5yo|9|0|0|
DE1|10|2|4|16:2,19:2
crimpo|11|2|6|9:3,10:3
MALAYA|12|2|6|12:3,11:3
Cole|13|2|4|13:1,14:3
Blue NINJA|14|2|5|15:3,16:2
Loading…|15|2|4|15:2,8:2
Aye|16|2|3|16:1,13:2
Kizaru|17|2|4|13:1,28:3
MR. ASURAN YT|18|2|6|18:3,19:3
SWAGMUFFIN90|19|0|0|
arius67'|20|2|6|7:3,8:3
MiniPekka|21|2|6|20:3,17:3
Brandon|22|2|5|22:2,26:3
Marrow|23|2|6|21:3,24:3
UNSTOPPABLE ADI|24|2|4|24:1,23:3
⚡️LSWreckless⚡️|25|2|5|25:3,26:2
Pharah|26|2|3|22:2,19:1
DandyPickle|27|2|4|22:2,16:2
F16|28|2|6|21:3,27:3
Stevie Wonder|29|2|5|22:3,16:2
MACK|30|2|6|33:3,29:3
pickledpigeon23|31|2|4|29:2,28:2
das|32|2|6|31:3,32:3
rinz|33|2|6|34:3,30:3
Tretor|34|0|0|
high|35|2|5|35:3,34:2"""),

("269536451","4/21/26","Bandung #1","35v35","""stage6yo|1|2|6|1:3,2:3
drybonez|2|2|6|5:3,4:3
PsychoHaze16|3|2|6|3:3,7:3
Americanpatriot|4|2|4|4:2,2:2
ridge|5|0|0|
Pam from HR|6|2|6|6:3,18:3
cameron|7|0|0|
crimpo|8|2|6|8:3,10:3
DE1|9|2|5|18:2,16:3
MALAYA|10|2|6|11:3,12:3
Cole|11|2|6|14:3,17:3
Blue NINJA|12|2|6|20:3,19:3
Loading…|13|2|4|13:1,9:3
Aye|14|2|6|15:3,13:3
Kizaru|15|2|4|15:1,32:3
Lowkey09|16|2|4|16:2,30:2
MR. ASURAN YT|17|2|5|21:3,2:2
SWAGMUFFIN90|18|2|4|6:2,7:2
Brandon|19|2|4|19:2,20:2
Lord-Aizen|20|0|0|
uhlisuh|21|2|4|21:2,26:2
MiniPekka|22|2|5|20:2,22:3
Marrow|23|2|6|23:3,24:3
UNSTOPPABLE ADI|24|2|3|22:2,20:1
Pharah|25|2|5|25:2,29:3
⚡️LSWreckless⚡️|26|2|6|26:3,25:3
Jack|27|0|0|
DandyPickle|28|2|5|27:3,26:2
Hey|29|1|3|31:3
Stevie Wonder|30|2|6|30:3,28:3
MACK|31|1|3|32:3
pickledpigeon23|32|2|4|35:3,24:1
das|33|2|6|33:3,32:3
rinz|34|0|0|
Tretor|35|2|5|30:3,28:2"""),

("269261532","4/19/26","КлАн НоГи","30v30","""stage6yo|1|2|5|1:2,2:3
Americanpatriot|2|2|4|1:1,2:3
Big Steppa|3|2|6|6:3,9:3
ridge|4|2|5|4:2,7:3
PsychoHaze16|5|2|6|5:3,3:3
Pam from HR|6|2|6|13:3,18:3
cameron|7|0|0|
crimpo|8|2|6|8:3,4:3
DE1|9|2|6|16:3,15:3
MALAYA|10|2|6|10:3,12:3
Jaedine|11|0|0|
Cole|12|2|5|15:3,10:2
Aye|13|2|2|1:1,2:1
Loading…|14|2|5|14:3,10:2
Kizaru|15|2|5|16:2,29:3
MR. ASURAN YT|16|2|5|12:2,25:3
studkiller|17|2|6|17:3,11:3
Brandon|18|2|5|18:2,22:3
Lord-Aizen|19|2|4|19:3,9:1
uhlisuh|20|2|6|20:3,23:3
MiniPekka|21|2|5|21:3,15:2
UNSTOPPABLE ADI|22|2|5|22:2,24:3
DandyPickle|23|2|4|23:2,29:2
⚡️LSWreckless⚡️|24|2|4|18:2,13:2
Stevie Wonder|25|2|6|27:3,28:3
MACK|26|2|6|26:3,30:3
tyraniann|27|0|0|
das|28|2|2|30:1,29:1
rinz|29|1|1|29:1
high|30|1|1|30:1"""),

("269062003","4/17/26","ASCEND","40v40","""stage6yo|1|2|6|1:3,2:3
Americanpatriot|2|2|5|4:2,3:3
Dragon|3|0|0|
Big Steppa|4|2|4|5:2,6:2
Pam from HR|5|2|6|16:3,11:3
crimpo|6|2|6|8:3,10:3
DE1|7|1|3|7:3
stage5yo|8|2|4|25:3,6:1
Jaedine|9|1|3|9:3
Blue NINJA|10|2|6|13:3,14:3
Cole|11|1|3|20:3
Aye|12|2|5|12:3,8:2
Loading…|13|2|4|13:2,11:2
Kizaru|14|1|2|14:2
Lowkey09|15|0|0|
MR. ASURAN YT|16|2|6|17:3,18:3
⚡ Fernando⚡|17|0|0|
SWAGMUFFIN90|18|0|0|
studkiller|19|1|3|15:3
Brandon|20|1|1|16:1
fortnite_justin|21|0|0|
BlurTrigr|22|0|0|
Lord-Aizen|23|2|6|23:3,22:3
uhlisuh|24|2|5|24:3,29:2
MiniPekka|25|2|5|21:3,20:2
Marrow|26|2|6|37:3,34:3
UNSTOPPABLE ADI|27|2|6|27:3,26:3
DandyPickle|28|2|5|28:3,25:2
Pharah|29|2|5|29:2,30:3
⚡️LSWreckless⚡️|30|2|6|29:3,33:3
Hey|31|2|6|32:3,36:3
Stevie Wonder|32|0|0|
MACK|33|2|6|39:3,38:3
pickledpigeon23|34|1|2|36:2
s.inman|35|2|6|35:3,31:3
tyraniann|36|1|2|40:2
das|37|1|2|40:2
rinz|38|2|3|7:1,40:2
Tretor|39|0|0|
high|40|1|0|40:0"""),

("268804808","4/15/26","SUPREMACÍA","30v30","""stage6yo|1|2|6|2:3,1:3
Americanpatriot|2|0|0|
Big Steppa|3|2|5|3:2,5:3
Pam from HR|4|2|5|4:3,3:2
crimpo|5|2|6|7:3,6:3
DE1|6|2|3|3:1,1:2
stage5yo|7|2|6|11:3,23:3
Blue NINJA|8|0|0|
Cole|9|0|0|
Aye|10|2|6|15:3,19:3
Loading…|11|2|5|10:3,8:2
Kizaru|12|2|6|12:3,25:3
Lowkey09|13|0|0|
MR. ASURAN YT|14|2|4|14:3,15:1
studkiller|15|2|6|13:3,9:3
Brandon|16|2|4|16:3,3:1
arius67'|17|2|6|17:3,8:3
BlurTrigr|18|2|4|18:3,3:1
MiniPekka|19|2|5|3:2,19:3
Pharah|20|2|4|20:1,21:3
⚡️LSWreckless⚡️|21|2|5|19:2,20:3
Hey|22|0|0|
Party|23|2|4|23:1,25:3
Stevie Wonder|24|2|6|24:3,22:3
pickledpigeon23|25|0|0|
MACK|26|2|6|26:3,28:3
s.inman|27|2|5|24:2,27:3
tyraniann|28|0|0|
das|29|2|5|19:2,25:3
rinz|30|2|6|30:3,29:3"""),

("268235660","4/9/26","The Nephalem","35v35","""stage6yo|1|2|5|2:3,1:2
Americanpatriot|2|1|3|7:3
Big Steppa|3|1|3|3:3
Pam from HR|4|2|6|4:3,6:3
stage5yo|5|2|6|5:3,19:3
DE1|6|2|6|13:3,18:3
Blue NINJA|7|2|1|1:0,7:1
Aye|8|2|5|5:2,10:3
Lowkey09|9|2|5|9:2,8:3
MR. ASURAN YT|10|2|4|6:1,5:3
SWAGMUFFIN90|11|0|0|
Brandon|12|2|5|13:2,15:3
BlurTrigr|13|2|4|5:3,4:1
studkiller|14|2|6|14:3,12:3
isaiah|15|0|0|
MiniPekka|16|2|6|16:3,11:3
Marrow|17|2|5|17:3,18:2
Jack|18|0|0|
krump|19|2|5|19:2,10:3
⚡️LSWreckless⚡️|20|2|6|20:3,9:3
Hey|21|1|3|24:3
F16|22|2|5|25:3,21:2
Pharah|23|2|6|23:3,22:3
dexd|24|0|0|
Party|25|2|6|21:3,29:3
pickledpigeon23|26|2|5|35:3,30:2
Stevie Wonder|27|2|6|28:3,30:3
MACK|28|2|6|27:3,26:3
Jihyo|29|1|3|29:3
tyraniann|30|0|0|
das|31|2|6|31:3,32:3
Tretor|32|0|0|
rinz|33|1|3|33:3
high|34|1|3|34:3
icyace|35|0|0|"""),

("268539352","4/12/26","ENDZONE","35v35","""stage6yo|1|2|6|1:3,2:3
Americanpatriot|2|2|5|2:3,1:2
Big Steppa|3|2|5|3:3,5:2
Pam from HR|4|1|3|4:3
crimpo|5|2|6|7:3,6:3
stage5yo|6|2|6|8:3,17:3
DE1|7|2|3|15:1,5:2
Blue NINJA|8|2|6|15:3,5:3
Cole|9|2|6|10:3,9:3
Aye|10|2|5|12:3,8:2
Kizaru|11|2|6|11:3,35:3
Lowkey09|12|2|3|12:2,22:1
MR. ASURAN YT|13|2|4|15:2,5:2
SWAGMUFFIN90|14|0|0|
Brandon|15|2|3|15:1,17:2
arius67'|16|2|6|14:3,13:3
BlurTrigr|17|2|2|15:1,5:1
studkiller|18|2|6|18:3,20:3
isaiah|19|0|0|
MiniPekka|20|2|6|19:3,22:3
DandyPickle|21|2|4|21:2,19:2
krump|22|2|3|17:1,15:2
⚡️LSWreckless⚡️|23|2|6|23:3,21:3
Hey|24|1|2|24:2
Pharah|25|2|6|25:3,24:3
F16|26|2|4|16:3,17:1
Stevie Wonder|27|2|6|26:3,30:3
dexd|28|0|0|
MACK|29|2|6|29:3,27:3
s.inman|30|2|6|28:3,31:3
Jihyo|31|1|1|15:1
tyraniann|32|0|0|
das|33|2|6|33:3,32:3
rinz|34|1|3|34:3
high|35|1|3|35:3"""),

("8LGRLVYU9","4/7/26","Exspan","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|2|2:2
Americanpatriot|3|1|3|3:3
Dragon|4|1|3|4:3
Pam from HR|5|1|3|5:3
stage5yo|6|1|3|6:3
DE1|7|1|3|7:3
Cole|8|1|3|8:3
Aye|9|1|3|9:3
Kizaru|10|1|3|10:3
MR. ASURAN YT|11|1|3|11:3
SWAGMUFFIN90|12|1|3|12:3
Brandon|13|1|3|13:3
arius67'|14|1|3|14:3
UNSTOPPABLE ADI|15|1|3|17:3
Marrow|16|1|3|16:3
Jack|17|1|3|17:3
DandyPickle|18|1|3|18:3
uhlisuh|19|1|3|19:3
Hey|20|1|3|20:3
Pharah|21|1|3|21:3
pickledpigeon23|22|1|3|22:3
MACK|23|1|3|23:3
Stevie Wonder|24|1|3|24:3
tyraniann|25|1|3|25:3
das|26|1|3|26:3
Tretor|27|1|3|27:3
rinz|28|1|3|28:3
high|29|1|3|29:3
icyace|30|1|3|30:3""", False, True),

("8LGQYCQQ2","4/6/26","الرعب","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|3|2:3
Americanpatriot|3|1|3|3:3
Dragon|4|1|3|4:3
Pam from HR|5|1|3|14:3
stage5yo|6|1|3|6:3
DE1|7|1|3|7:3
Cole|8|1|3|9:3
Aye|9|1|3|12:3
Kizaru|10|1|3|10:3
MR. ASURAN YT|11|1|3|11:3
SWAGMUFFIN90|12|1|3|24:3
Brandon|13|1|3|13:3
arius67'|14|1|3|5:3
UNSTOPPABLE ADI|15|1|3|15:3
Marrow|16|1|3|16:3
Jack|17|1|3|17:3
DandyPickle|18|1|3|18:3
uhlisuh|19|1|3|19:3
Hey|20|1|3|20:3
pickledpigeon23|21|1|3|21:3
MACK|22|1|3|22:3
Stevie Wonder|23|1|3|23:3
Sen|24|1|3|8:3
tyraniann|25|0|0|
das|26|1|3|26:3
Tretor|27|1|3|27:3
rinz|28|1|0|28:0
high|29|1|3|29:3
icyace|30|1|3|30:3""", False, True),

("8LGY9RLGQ","4/5/26","123","30v30","""stage6yo|1|1|3|6:3
drybonez|2|1|3|2:3
Americanpatriot|3|1|3|3:3
Dragon|4|1|3|4:3
Pam from HR|5|1|3|5:3
stage5yo|6|1|3|7:3
DE1|7|1|3|19:3
Cole|8|1|2|8:2
Aye|9|1|2|9:2
Loading…|10|1|3|10:3
Kizaru|11|1|2|11:2
MR. ASURAN YT|12|1|3|12:3
SWAGMUFFIN90|13|0|0|
Brandon|14|1|3|14:3
arius67'|15|1|3|15:3
BlurTrigr|16|1|3|16:3
isaiah|17|0|0|
studkiller|18|1|2|18:2
UNSTOPPABLE ADI|19|1|0|19:0
DandyPickle|20|1|2|20:2
Jack|21|1|2|21:2
Marrow|22|1|3|22:3
uhlisuh|23|1|2|23:2
MiniPekka|24|1|3|24:3
krump|25|1|3|25:3
⚡️LSWreckless⚡️|26|1|3|26:3
Pharah|27|1|3|27:3
pickledpigeon23|28|1|3|28:3
Party|29|1|3|29:3
Stevie Wonder|30|1|3|30:3""", False, True),

("8LG98L2PC","4/4/26","Mndo Kediri","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|1|2:1
Americanpatriot|3|1|3|7:3
Dragon|4|1|3|12:3
Pam from HR|5|1|2|5:2
DE1|6|1|3|6:3
Cole|7|1|1|7:1
Aye|8|1|3|8:3
Loading…|9|1|3|9:3
Kizaru|10|1|3|11:3
arius67'|11|1|3|10:3
Brandon|12|1|1|12:1
BlurTrigr|13|1|3|13:3
isaiah|14|1|3|14:3
studkiller|15|1|3|15:3
UNSTOPPABLE ADI|16|1|3|16:3
DandyPickle|17|1|3|17:3
Jack|18|1|3|18:3
Marrow|19|1|3|19:3
uhlisuh|20|1|3|20:3
MiniPekka|21|1|3|21:3
krump|22|1|3|22:3
⚡️LSWreckless⚡️|23|1|3|23:3
Pharah|24|1|3|24:3
pickledpigeon23|25|1|3|25:3
Stevie Wonder|26|1|3|26:3
Party|27|1|3|27:3
MACK|28|1|3|28:3
rinz|29|1|3|29:3
high|30|1|3|30:3""", False, True),

("8LG0VRGUQ","4/3/26","Excessive Force","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|2|2:2
Americanpatriot|3|1|3|3:3
Dragon|4|1|3|4:3
Pam from HR|5|1|3|5:3
DE1|6|1|3|6:3
Blue NINJA|7|0|0|
Cole|8|1|2|8:2
Aye|9|1|2|9:2
Loading…|10|1|2|10:2
Kizaru|11|1|3|11:3
SWAGMUFFIN90|12|1|3|12:3
arius67'|13|1|3|13:3
BlurTrigr|14|1|3|14:3
isaiah|15|1|3|15:3
studkiller|16|1|3|16:3
Brandon|17|1|3|17:3
UNSTOPPABLE ADI|18|1|1|18:1
Jack|19|1|3|19:3
Marrow|20|1|2|20:2
uhlisuh|21|1|2|21:2
MiniPekka|22|1|3|22:3
krump|23|1|3|23:3
⚡️LSWreckless⚡️|24|1|3|24:3
Pharah|25|1|3|25:3
pickledpigeon23|26|1|1|26:1
Stevie Wonder|27|1|3|27:3
MACK|28|1|3|28:3
Party|29|1|3|29:3
rinz|30|1|3|30:3""", False, True),

("8LQUVPLJ9","4/2/26","ملوك كلاش","30v30","""stage6yo|1|1|3|1:3
drybonez|2|1|3|2:3
Americanpatriot|3|1|3|3:3
Dragon|4|1|3|4:3
Pam from HR|5|1|3|27:3
DE1|6|1|3|6:3
Blue NINJA|7|1|3|7:3
Aye|8|1|3|8:3
Loading…|9|1|3|9:3
Kizaru|10|1|3|10:3
arius67'|11|1|3|11:3
isaiah|12|1|3|12:3
studkiller|13|1|3|13:3
Brandon|14|1|3|14:3
UNSTOPPABLE ADI|15|1|3|15:3
$$BLAZE KING$$|16|0|0|
DandyPickle|17|1|3|17:3
uhlisuh|18|1|3|18:3
cypher|19|1|3|19:3
MiniPekka|20|1|3|20:3
krump|21|1|3|21:3
⚡️LSWreckless⚡️|22|1|3|22:3
dexd|23|0|0|
Pharah|24|1|3|24:3
pickledpigeon23|25|1|3|25:3
Party|26|1|3|26:3
Sen|27|1|2|5:2
s.inman|28|1|3|28:3
rinz|29|1|3|29:3
high|30|1|3|30:3""", False, True),

("8LQCG02G9","4/1/26","indian army new","30v30","""stage6yo|1|1|2|1:2
drybonez|2|1|2|2:2
Americanpatriot|3|1|1|3:1
Dragon|4|1|2|4:2
Pam from HR|5|1|2|5:2
stage5yo|6|1|2|6:2
DE1|7|1|2|7:2
Blue NINJA|8|1|1|8:1
Cole|9|1|1|9:1
Aye|10|1|2|10:2
Loading…|11|1|2|11:2
Kizaru|12|1|2|12:2
MR. ASURAN YT|13|1|2|13:2
SWAGMUFFIN90|14|1|3|27:3
arius67'|15|1|3|15:3
isaiah|16|1|3|16:3
BlurTrigr|17|1|2|17:2
studkiller|18|1|3|18:3
UNSTOPPABLE ADI|19|1|1|19:1
DandyPickle|20|1|3|20:3
Jack|21|1|2|21:2
Marrow|22|1|2|22:2
MiniPekka|23|1|2|23:2
uhlisuh|24|1|3|24:3
krump|25|1|3|25:3
⚡️LSWreckless⚡️|26|1|3|26:3
CLASHER ADITYA|27|0|0|
Pharah|28|1|3|28:3
Stevie Wonder|29|1|3|29:3
Party|30|1|3|30:3""", False, True),

("267804602","3/30/26","MABAR VIP","40v40","""stage6yo|1|2|6|1:3,2:3
drybonez|2|2|6|3:3,4:3
Americanpatriot|3|2|6|5:3,6:3
Dragon|4|2|6|22:3,27:3
Pam from HR|5|2|6|7:3,8:3
stage5yo|6|2|4|6:3,1:1
DE1|7|2|3|1:1,2:2
Blue NINJA|8|2|6|9:3,10:3
Cole|9|2|5|8:2,4:3
Aye|10|2|6|12:3,29:3
Kizaru|11|2|5|11:3,12:2
MR. ASURAN YT|12|2|6|15:3,17:3
SWAGMUFFIN90|13|2|5|14:3,9:2
Loading…|14|2|4|13:3,12:1
BlurTrigr|15|2|4|15:1,14:3
studkiller|16|2|4|16:3,11:1
Brandon|17|2|3|17:2,15:1
UNSTOPPABLE ADI|18|2|6|19:3,18:3
arius67'|19|2|5|5:2,30:3
DandyPickle|20|2|5|20:2,19:3
$BLAZE KING$|21|0|0|
EMAN|22|0|0|
Marrow|23|2|6|23:3,21:3
MiniPekka|24|2|5|24:3,22:2
krump|25|2|6|25:3,20:3
uhlisuh|26|2|6|26:3,36:3
dexd|27|1|3|33:3
CLASHER ADITYA|28|0|0|
Hey|29|1|3|32:3
pickledpigeon23|30|2|2|30:1,29:1
Pharah|31|2|6|38:3,40:3
Stevie Wonder|32|1|3|40:3
MACK|33|2|5|31:3,33:2
Sen|34|2|4|28:3,27:1
s.inman|35|2|4|36:1,37:3
tyraniann|36|0|0|
das|37|2|6|35:3,34:3
Tretor|38|1|1|2:1
rinz|39|2|5|39:3,38:2
high|40|1|3|40:3"""),

("267573823","3/28/26","Infiniti Power","40v40","""stage6yo|1|2|4|1:1,2:3
Americanpatriot|2|2|2|1:1,3:1
drybonez|3|2|5|4:2,6:3
Dragon|4|2|6|4:3,5:3
Pam from HR|5|2|5|17:3,3:2
stage5yo|6|2|6|7:3,9:3
DE1|7|2|4|5:2,4:2
Blue NINJA|8|2|6|14:3,12:3
Cole|9|1|0|3:0
Aye|10|2|4|10:3,13:1
Kizaru|11|2|6|11:3,15:3
MR. ASURAN YT|12|2|6|21:3,27:3
Loading…|13|2|6|10:3,16:3
isaiah|14|0|0|
BlurTrigr|15|2|5|15:2,18:3
studkiller|16|2|6|31:3,40:3
Brandon|17|2|2|17:1,18:1
UNSTOPPABLE ADI|18|2|6|19:3,13:3
DandyPickle|19|1|3|19:3
arius67'|20|2|6|20:3,8:3
$$BLAZE KING$$|21|2|5|21:2,22:3
EMAN|22|2|6|33:3,34:3
Jack|23|0|0|
Marrow|24|2|6|24:3,23:3
uhlisuh|25|2|5|25:3,17:2
MiniPekka|26|2|6|28:3,30:3
F16|27|0|0|
CLASHER ADITYA|28|0|0|
⚡️LSWreckless⚡️|29|2|6|29:3,26:3
Hey|30|1|1|32:1
pickledpigeon23|31|2|3|38:2,37:1
Pharah|32|2|5|31:2,32:3
Amir|33|0|0|
Stevie Wonder|34|2|4|3:1,40:3
MACK|35|2|6|38:3,35:3
Sen|36|1|3|39:3
s.inman|37|2|6|36:3,37:3
das|38|2|4|22:1,38:3
Tretor|39|0|0|
rinz|40|1|3|40:3"""),
]

# ── Win/Loss/Draw results keyed by war ID ──
RESULTS = {
    '273131437': 'W',  # Friendj of wer
    '272906647': 'D',  # ⚡INDIAN KINGDOM
    '272696863': 'W',  # SARYAGAW
    '272454773': 'L',  # UNITY ID
    '272138237': 'W',  # INVADERS
    '271917758': 'W',  # Tyran
    '271683120': 'W',  # Aikatsu likes
    '271426618': 'W',  # GEMBOX PATCH
    '271225938': 'D',  # 12 DEC 2021
    '270965373': 'W',  # MiniMalizM
    '270475341': 'D',  # GOAT
    '270286010': 'W',  # Krasavchiki
    '270045813': 'W',  # Bangladesh kin
    '269790839': 'W',  # البارون
    '269536451': 'W',  # Bandung #1
    '269261532': 'W',  # КлАн НоГи
    '269062003': 'L',  # ASCEND
    '268804808': 'W',  # SUPREMACÍA
    '268539352': 'D',  # ENDZONE
    '268235660': 'W',  # The Nephalem
    '267804602': 'W',  # MABAR VIP
    '267573823': 'W',  # Infiniti Power
    # CWL current season
    '217372345': 'W',  # Bama Boyz (Round 1, 6/2/26)
    # CWL — Buzzzzz 1st in both seasons
    '8Q0J0022Q': 'W', '8Q0G02CGY': 'W', '8Q0L0VR82': 'W', '8Q0P0CYLR': 'W',
    '8Q0882R82': 'W', '8Q0020RCC': 'W', '8LVUPY0R9': 'W',
    '8LGRLVYU9': 'W', '8LGQYCQQ2': 'W', '8LGY9RLGQ': 'W', '8LG98L2PC': 'W',
    '8LG0VRGUQ': 'W', '8LQUVPLJ9': 'W', '8LQCG02G9': 'W',
}

def parse_atk_detail(raw_attacks, v2=False):
    """Parse attack detail string into list. v2: [defPos,rawStars,delta,defTH], v1: [defPos,stars]."""
    detail = []
    if not raw_attacks:
        return detail
    for pair in raw_attacks.split(','):
        p = pair.split(':')
        if v2 and len(p) == 4:
            detail.append([p[0], int(p[1]), int(p[2]), int(p[3])])
        elif len(p) >= 2:
            # v1 or partial — delta/defTH default to 0
            detail.append([p[0], int(p[1]), 0, 0])
    return detail

def parse_war(war_id, date, opp, size, raw, in_prog=False, cwl=False):
    players = {}
    for line in raw.strip().split('\n'):
        parts = line.split('|')
        if parts[0].startswith('#'):
            # ── V2 format: #tag|name|pos|TH|atk_count|raw_stars|net_stars|attacks ──
            if len(parts) < 7:
                continue
            tag      = parts[0]
            name     = parts[1]
            pos      = int(parts[2])
            th       = int(parts[3]) if parts[3] else 0
            atks     = int(parts[4])
            stars    = int(parts[5])
            net_stars= int(parts[6]) if parts[6] else stars
            atk_detail = parse_atk_detail(parts[7] if len(parts) > 7 else '', v2=True)
            players[tag] = {'p': pos, 'th': th, 'a': atks, 's': stars, 'ns': net_stars,
                            'atks': atk_detail, 'name': name}
        else:
            # ── V1 format: name|pos|atk_count|total_stars|attacks ──
            if len(parts) < 4:
                continue
            name = parts[0]
            pos  = int(parts[1])
            atks = int(parts[2])
            stars= int(parts[3])
            atk_detail = parse_atk_detail(parts[4] if len(parts) > 4 else '')
            players[name] = {'p': pos, 'a': atks, 's': stars, 'atks': atk_detail}
    return {
        'id': war_id,
        'date': date,
        'opp': opp,
        'size': size,
        'players': players,
        'in_prog': in_prog,
        'cwl': cwl,
        'result': RESULTS.get(war_id, '')
    }

wars = [parse_war(*b) for b in WAR_BLOCKS]

# Seed all_players:
# - V1 players (name-keyed) seeded from ACTIVE set
# - V2 players (tag-keyed, starts with #) seeded from PLAYER_TAGS
all_players = {}
for name in ACTIVE:
    all_players[name] = {'active': True}
for tag, name in PLAYER_TAGS.items():
    if tag not in all_players:
        all_players[tag] = {'active': name in ACTIVE, 'name': name}

# Then add anyone else seen in wars (ex-members, historical players, etc.)
for w in wars:
    for key, data in w['players'].items():
        if key not in all_players:
            if key.startswith('#'):
                display = data.get('name', key)
                all_players[key] = {'active': display in ACTIVE, 'name': display}
            else:
                all_players[key] = {'active': key in ACTIVE}

# ── 60-day window ──
_today = datetime.now()
_cutoff = _today - timedelta(days=60)

def _parse_war_date(date_str):
    try:
        p = date_str.split('/')
        y = int(p[2]); y = y + 2000 if y < 100 else y
        return datetime(y, int(p[0]), int(p[1]))
    except Exception:
        return _today

# ── Canonical member key resolution (tag > name) ──
_name_to_tag = {name: tag for tag, name in PLAYER_TAGS.items()}

_members = {}
for _key, _info in all_players.items():
    if _key.startswith('#'):
        _name = _info.get('name', _key); _canonical = _key
    else:
        _name = _key; _canonical = _name_to_tag.get(_name, _name)
    if _canonical not in _members:
        _members[_canonical] = {
            'name': _name,
            'status': 'active' if _info.get('active', _name in ACTIVE) else 'left',
            'th': 0, 'cells': {}
        }

# ── Build wars_data + cells ──
_wars_data = []
for _war in wars:
    _is_v2 = any(k.startswith('#') for k in _war['players'].keys())
    _war_dt = _parse_war_date(_war['date'])
    _in_window = _war_dt >= _cutoff
    _rc = _war['result']
    if _war['in_prog']:      _result = 'live'
    elif _rc == 'W':         _result = 'win'
    elif _rc == 'L':         _result = 'loss'
    elif _rc == 'D':         _result = 'draw'
    else:                    _result = 'draw'
    _dp = _war['date'].split('/')
    _date_disp = f"{_dp[0]}/{_dp[1]}" if len(_dp) >= 2 else _war['date']
    _wars_data.append({
        'id': _war['id'], 'date': _date_disp, 'name': _war['opp'],
        'size': _war['size'], 'result': _result, 'cwl': _war['cwl'],
        'pending': _war['in_prog'], 'v2': _is_v2, 'inWindow': _in_window
    })
    _max_atk = 1 if _war['cwl'] else 2
    for _pkey, _pd in _war['players'].items():
        if _pkey.startswith('#'):
            _canonical = _pkey; _pname = _pd.get('name', _pkey)
        else:
            _canonical = _name_to_tag.get(_pkey, _pkey); _pname = _pkey
        if _canonical not in _members:
            _active = _pname in ACTIVE or _pkey in ACTIVE
            _members[_canonical] = {'name': _pname, 'status': 'active' if _active else 'left', 'th': 0, 'cells': {}}
        if _is_v2 and _pd.get('th', 0) > 0 and _members[_canonical]['th'] == 0:
            _members[_canonical]['th'] = _pd['th']
        _used = _pd.get('a', 0)
        _atk_th = _pd.get('th', None) if _is_v2 else None
        if _war['in_prog'] and _used == 0:
            _members[_canonical]['cells'][_war['id']] = {'pending': True}; continue
        _attacks = []
        for _a in _pd.get('atks', []):
            try: _to = int(_a[0])
            except: _to = str(_a[0])
            _a_def_th = _a[3] if (len(_a) > 3 and _is_v2) else None
            _th_delta = (_a_def_th - _atk_th) if (_is_v2 and _a_def_th and _atk_th) else 0
            _atk_obj = {'to': _to, 'raw': _a[1], 'neu': _a[2]}
            if _is_v2:
                _atk_obj.update({'defTh': _a_def_th, 'delta': _th_delta, 'atkTh': _atk_th})
            _attacks.append(_atk_obj)
        _comp_raw = sum(_a['raw'] for _a in _attacks)
        _comp_net = sum(_a['neu'] for _a in _attacks) if _is_v2 else _comp_raw
        _cell = {
            'inWar': True, 'used': _used, 'max': _max_atk, 'attacks': _attacks,
            'cwl': _war['cwl'], 'missed': _max_atk - _used, 'v2': _is_v2,
            'rawStars': _comp_raw, 'netStars': _comp_net,
            'stars': _comp_net if _is_v2 else _comp_raw,
            'pos': _pd.get('p', '?')
        }
        if _atk_th is not None: _cell['atkTh'] = _atk_th
        _members[_canonical]['cells'][_war['id']] = _cell

# ── Per-member aggregates (60-day window only, excl CWL + pending) ──
_in_window_set    = {_wd['id'] for _wd in _wars_data if _wd['inWindow'] and not _wd['pending'] and not _wd.get('cwl', False)}
_cwl_finished_set = {_wd['id'] for _wd in _wars_data if _wd['inWindow'] and not _wd['pending'] and _wd.get('cwl', False)}
_members_list = []
for _canonical, _member in _members.items():
    _pl = _el = _ms = _st = _us = _av = _sd = _ac = _di = _re = _rw = _nt = _v2a = 0
    # Collect window wars in newest-first order (WAR_BLOCKS order)
    _ww = [(_w, _member['cells'].get(_w['id']))
           for _w in wars
           if not _w['cwl'] and not _w['in_prog'] and _w['id'] in _in_window_set]
    # If member appears in any archived (out-of-window) war they predate the window
    # → all window wars are eligible. Otherwise find first appearance in window.
    _predates_window = any(
        _member['cells'].get(_w['id']) is not None
        for _w in wars
        if not _w['cwl'] and not _w['in_prog'] and _w['id'] not in _in_window_set
    )
    if _predates_window:
        _first_idx = len(_ww) - 1  # use all window wars
    else:
        _first_idx = next((i for i in range(len(_ww)-1, -1, -1)
                           if _ww[i][1] is not None and not _ww[i][1].get('pending')), None)
    if _first_idx is not None:
        for _war, _cell in _ww[:_first_idx + 1]:
            _el += 1  # all wars since member's first appearance
            if _cell is None or _cell.get('pending'): continue
            if _cell.get('used', 0) > 0: _pl += 1
            _ms += (1 if _cell.get('used', 0) == 0 else 0); _st += _cell.get('stars', 0)
            _us += _cell.get('used', 0); _av += _cell.get('max', 0)
            _rw += _cell.get('rawStars', 0); _nt += _cell.get('netStars', 0)
            for _a in (_cell.get('attacks', []) if _cell else []):
                if 'defTh' not in _a or _a['defTh'] is None: continue
                _d = _a.get('delta', 0); _sd += _d; _ac += 1; _v2a += 1
                if _d < 0: _di += 1
                elif _d > 0: _re += 1
    # CWL misses: excluded from participation/eligible but still count toward missed total
    for _war in wars:
        if not _war['cwl'] or _war['in_prog'] or _war['id'] not in _cwl_finished_set:
            continue
        _cell = _member['cells'].get(_war['id'])
        if _cell is None or _cell.get('pending'):
            continue  # not in this CWL round
        if _cell.get('used', 0) == 0:
            _ms += 1
    _pname = _member['name']
    _th_val = _member['th'] or PLAYER_TH.get(_pname, 0)  # API data first; PLAYER_TH as fallback only when API returns 0
    _cs_rank = _CS_RANK.get(_pname, 999)
    _members_list.append({
        'name': _pname, 'th': _th_val, 'thRank': _cs_rank, 'status': _member['status'],
        'cells': _member['cells'], 'played': _pl, 'eligible': _el, 'missed': _ms,
        'stars': _st, 'used': _us, 'available': _av,
        'participation': _pl / _el if _el else 0,
        'hitRate': _us / _av if _av else 0,
        'sumDelta': _sd, 'atkCount': _ac, 'dips': _di, 'reaches': _re,
        'wasted': 0, 'v2atks': _v2a, 'rawStars': _rw, 'netStars': _nt,
        'avgDelta': _sd / _ac if _ac else 0
    })

_archived_count = sum(1 for _wd in _wars_data if not _wd['inWindow'] and not _wd['pending'])
_meta = {
    'clanName': 'Buzzzzz', 'clanTag': '#2GGL80JL0', 'windowDays': 60,
    'windowLabel': f"{_cutoff.strftime('%-m/%-d')} – {_today.strftime('%-m/%-d/%y')}",
    'archivedWars': _archived_count,
    'updated': _today.strftime('%-m/%-d/%y'),
    'warEndISO': WAR_END_ISO,
}

print(f"// Players: {len(_members_list)}")
print(f"// Wars: {len(_wars_data)} ({sum(1 for w in _wars_data if w['inWindow'])} in window)")
print("DATA OK")

_wardata_json = json.dumps({'meta': _meta, 'wars': _wars_data, 'members': _members_list},
                           ensure_ascii=False, separators=(',', ':'))


_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Buzzzzz War Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Oswald:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
:root{
  --bg:#0a0d0a;--surface:#11150f;--surface2:#0d110c;--surface3:#161c14;
  --ink:#e8eee2;--muted:#8a9484;--faint:#5d655a;
  --line:#222a20;--line2:#2d362a;
  --star:#e3a92b;
  --full-bg:oklch(0.345 0.085 152);--full-tx:oklch(0.88 0.13 150);--full-bd:oklch(0.45 0.09 152);
  --part-bg:oklch(0.40 0.085 82);--part-tx:oklch(0.90 0.12 88);--part-bd:oklch(0.50 0.09 82);
  --miss-bg:oklch(0.40 0.145 28);--miss-tx:oklch(0.88 0.12 30);--miss-bd:oklch(0.52 0.16 28);
  --none-bg:#0e120d;--none-tx:#39402f;
  --live-bg:oklch(0.40 0.09 244);--live-tx:oklch(0.88 0.1 244);--live-bd:oklch(0.5 0.1 244);
  --reach-bg:oklch(0.40 0.09 244);--reach-tx:oklch(0.86 0.12 244);
  --dip-bg:oklch(0.43 0.11 56);--dip-tx:oklch(0.88 0.13 56);
  --accent:#e3a92b;
  --hf:'Oswald',sans-serif;--bf:'JetBrains Mono',monospace;--mf:'JetBrains Mono',monospace;
  --bg-grid:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--bf);-webkit-font-smoothing:antialiased;
     display:flex;flex-direction:column;overflow:hidden;
     background-image:var(--bg-grid);background-size:46px 46px}
.mono{font-family:var(--mf);font-variant-numeric:tabular-nums}
/* header */
header{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;
       padding:16px 22px;border-bottom:1px solid var(--line);flex-wrap:wrap;
       background:linear-gradient(180deg,var(--surface3),var(--surface))}
.brand{display:flex;align-items:center;gap:12px}
.crest{width:38px;height:38px;display:grid;place-items:center;font-weight:700;font-size:17px;
       background:transparent;border:1px solid var(--star);color:var(--star);
       font-family:'Oswald';clip-path:polygon(0 0,100% 0,100% 76%,76% 100%,0 100%)}
.brand h1{font-family:var(--hf);font-size:19px;font-weight:600;letter-spacing:1px;text-transform:uppercase;line-height:1;white-space:nowrap}
.brand .sub{font-size:12px;color:var(--muted);margin-top:3px;white-space:nowrap}
.htools{display:flex;align-items:center;gap:18px}
.claninfo{text-align:right;font-size:12px;color:var(--muted);line-height:1.5;white-space:nowrap}
.claninfo b{color:var(--ink);font-weight:600}
/* strip */
.strip{flex:0 0 auto;display:flex;gap:0;border-bottom:1px solid var(--line);background:var(--surface2)}
.kpi{padding:12px 22px;border-right:1px solid var(--line);display:flex;flex-direction:column;gap:3px;min-width:130px}
.kpi .k{font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:600;display:flex;gap:6px;align-items:center}
.kpi .v{font-family:var(--hf);font-size:26px;font-weight:600;line-height:1;letter-spacing:-.5px}
.kpi .u{font-size:11.5px;color:var(--faint)}
.kpi.alert .v{color:var(--miss-tx)}.kpi.alert .k{color:var(--miss-tx)}
.pelt{width:8px;height:8px;border-radius:2px}
/* controls */
.controls{flex:0 0 auto;display:flex;align-items:center;gap:16px;padding:11px 22px;border-bottom:1px solid var(--line);
          background:var(--surface);flex-wrap:wrap}
.cgroup{display:flex;align-items:center;gap:8px}
.clab{font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);font-weight:600}
.seg{display:inline-flex;background:var(--surface2);border:1px solid var(--line2);border-radius:8px;padding:2px;gap:2px}
.seg button{border:0;background:transparent;font-family:var(--bf);font-size:12.5px;font-weight:500;color:var(--muted);
            padding:6px 11px;border-radius:6px;cursor:pointer;transition:.14s;white-space:nowrap}
.seg button:hover{color:var(--ink)}
.seg button[aria-pressed="true"]{background:var(--star);color:#1a1505;font-weight:600}
.spacer{flex:1 1 auto}
.legend{display:flex;align-items:center;gap:13px;flex-wrap:wrap}
.leg{display:flex;align-items:center;gap:6px;font-size:11.5px;color:var(--muted);white-space:nowrap}
.swatch{width:15px;height:15px;border-radius:4px;border:1px solid}
.swatch.full{background:var(--full-bg);border-color:var(--full-bd)}
.swatch.part{background:var(--part-bg);border-color:var(--part-bd)}
.swatch.miss{background:var(--miss-bg);border-color:var(--miss-bd)}
.swatch.live{background:var(--live-bg);border-color:var(--live-bd)}
.swatch.none{background:var(--none-bg);border-color:var(--line2)}
/* matrix */
.matrix{position:relative;flex:1 1 auto;min-height:0}
.scroll{position:absolute;inset:0;overflow:auto;background:var(--bg);scroll-behavior:smooth}
.scrbtn{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;
        background:var(--surface2);border:1px solid var(--line2);border-radius:6px;
        color:var(--muted);cursor:pointer;transition:background .12s,color .12s,border-color .12s}
.scrbtn:hover:not([disabled]){background:var(--surface3);color:var(--star);border-color:var(--star)}
.scrbtn[disabled]{opacity:.3;pointer-events:none}
.scrbtn svg{width:13px;height:13px}
table{border-collapse:separate;border-spacing:0}
thead th{position:sticky;top:0;z-index:5}
/* war header */
th.wh{width:var(--warcol-w,80px);min-width:var(--warcol-w,80px);vertical-align:top;padding:8px 6px 9px;text-align:center;cursor:pointer;user-select:none;
      background:var(--surface2);border-right:1px solid var(--line);border-bottom:1px solid var(--line2)}
th.wh .whrow{display:flex;align-items:center;justify-content:center;gap:5px}
th.wh .wdate{font-family:var(--hf);font-weight:700;font-size:13px;color:var(--star);letter-spacing:-.2px}
th.wh .cwl{font-size:8px;font-weight:700;letter-spacing:.04em;color:var(--accent);border:1px solid var(--accent);
            padding:0 3px;border-radius:3px;line-height:1.4}
th.wh .wd{font-size:10px;color:var(--faint);margin-top:3px;font-family:var(--mf)}
th.wh .wnm{font-size:10.5px;color:var(--muted);margin-top:4px;font-weight:600;white-space:nowrap}
th.wh .wmeta{display:flex;align-items:center;justify-content:center;gap:4px;margin-top:5px}
th.wh .wsz{font-size:9px;color:var(--faint);font-family:var(--mf)}
th.wh .wres{font-size:8.5px;font-weight:700;letter-spacing:.03em;padding:1px 4px;border-radius:3px}
.wres.win{color:var(--full-tx);background:var(--full-bg)}
.wres.loss{color:var(--miss-tx);background:var(--miss-bg)}
.wres.draw{color:var(--muted);background:var(--surface3)}
.wres.live{color:var(--live-tx);background:var(--live-bg)}
th.wh:hover{background:color-mix(in oklab,var(--star) 8%,var(--surface2))}
th.wh.focused{background:color-mix(in oklab,var(--star) 18%,var(--surface2));box-shadow:inset 0 -2px 0 var(--star)}
th.wh.focused .wdate{color:var(--ink)}
th.wh.iscwl{background:color-mix(in oklab,var(--accent) 7%,var(--surface2))}
th.wh.archived{opacity:.42}
/* archived column separator */
th.wh.arc-start{border-left:2px solid #4a3f2a!important}
td.cell.arc-start{border-left:2px solid #4a3f2a!important}
/* sticky corners */
th.pcorner,th.mcorner{background:var(--surface2);border-bottom:1px solid var(--line2);vertical-align:bottom;
                      text-align:left;padding:10px 14px;z-index:7}
th.pcorner{left:0;width:190px;min-width:190px}
th.mcorner{left:190px;width:72px;min-width:72px;border-right:1px solid var(--line2);text-align:center;padding:10px 6px}
th.pcorner .t{font-family:var(--hf);font-size:13px;font-weight:700;color:var(--star);text-transform:uppercase;letter-spacing:.04em}
th.pcorner .s{font-size:10px;color:var(--faint);margin-top:2px}
th.mcorner .t{font-family:var(--hf);font-size:11px;font-weight:700;color:var(--star);text-transform:uppercase;letter-spacing:.04em}
th.mcorner .s{font-size:9px;color:var(--faint)}
td.pcol,td.mcol{position:sticky;z-index:4;background:var(--surface)}
td.pcol{left:0;width:190px;min-width:190px;padding:8px 14px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
td.mcol{left:190px;width:72px;min-width:72px;text-align:center;border-right:1px solid var(--line2);border-bottom:1px solid var(--line)}
tr:hover td.pcol,tr:hover td.mcol{background:var(--surface3)}
.pname{font-family:'Oswald';font-weight:500;font-size:14.5px;letter-spacing:.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pmeta{display:flex;align-items:center;gap:7px;margin-top:3px}
.badge{font-size:9px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:1px 5px;border-radius:4px}
.badge.active{color:var(--full-tx);background:var(--full-bg)}
.badge.left{color:var(--miss-tx);background:var(--miss-bg)}
.thbadge{font-size:9px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:1px 5px;border-radius:4px;
         color:oklch(0.88 0.12 244);background:oklch(0.32 0.07 244)}
.pw{font-size:11px;color:var(--faint);font-family:var(--mf)}
.mval{display:inline-grid;place-items:center;min-width:26px;height:26px;padding:0 7px;border-radius:7px;
      font-family:var(--mf);font-weight:600;font-size:14px}
.mval.h0{color:var(--faint)}
.mval.h1{color:oklch(0.92 0.16 88);background:oklch(0.36 0.09 85)}
.mval.h2{color:oklch(0.90 0.18 48);background:oklch(0.38 0.13 44)}
.mval.h3{color:oklch(0.94 0.16 22);background:var(--miss-bg);border:1.5px solid var(--miss-bd)}
/* data cells */
td.cell{width:var(--warcol-w,80px);min-width:var(--warcol-w,80px);height:46px;text-align:center;border-right:1px solid var(--line);
        border-bottom:1px solid var(--line);padding:3px 4px;vertical-align:middle;transition:height .14s}
td.cell.full{background:var(--full-bg)}
td.cell.part{background:var(--part-bg)}
td.cell.miss{background:var(--miss-bg)}
td.cell.none{background:var(--none-bg)}
td.cell.live{background:var(--live-bg)}
td.cell.archived{opacity:.42}
.cmain{display:flex;align-items:baseline;justify-content:center;gap:5px;line-height:1.1}
.cmain .ua{font-family:var(--mf);font-size:12px;color:var(--muted);font-weight:500}
.cmain .st{font-family:var(--mf);font-size:13.5px;font-weight:600;color:var(--star)}
td.cell.full .ua{color:var(--full-tx)}
td.cell.part .ua{color:var(--part-tx)}
.cmain .mx{font-family:var(--hf);font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--miss-tx)}
td.cell.live .lv{font-size:10px;font-weight:700;letter-spacing:.05em;color:var(--live-tx)}
td.cell.none .dash{color:var(--none-tx);font-size:14px}
.cd{display:none;margin-top:3px;font-family:var(--mf);font-size:9.5px;color:var(--muted);line-height:1.4}
.ato{color:var(--faint);font-size:8px}
td.cell.miss .cd{color:var(--miss-tx)}
.cd .dd{font-weight:700}
.cd .dd.up{color:var(--reach-tx)}.cd .dd.dip{color:var(--dip-tx)}.cd .dd.even{color:var(--faint)}
.cdelta{display:none;gap:4px;justify-content:center;align-items:center;margin-top:4px;flex-wrap:wrap}
.dch{font-family:var(--mf);font-size:10px;font-weight:700;padding:1px 5px;border-radius:5px;line-height:1.4;letter-spacing:-.02em}
.dch.up{color:var(--reach-tx);background:var(--reach-bg)}
.dch.dip{color:var(--dip-tx);background:var(--dip-bg)}
.dch.even{color:var(--faint);background:transparent;font-weight:500;opacity:.55;padding:1px 2px}
.dch.na{color:var(--faint);background:transparent;opacity:.5;font-size:8.5px;font-weight:500;letter-spacing:0}
.clean{font-size:10px;color:var(--dip-tx);margin-left:2px;cursor:help}
.cd .raw{color:var(--faint)}.cd .zero{color:var(--dip-tx);font-weight:700}
th.wh .v2dot{width:5px;height:5px;border-radius:50%;background:var(--reach-tx);display:inline-block}
th.wh .v1tag{font-size:7.5px;font-weight:700;letter-spacing:.04em;color:var(--faint);opacity:.7}
table.view-delta td.cell{height:62px}
table.view-delta .cdelta{display:flex}
table.view-full td.cell{height:76px}
table.view-full .cd{display:block}
.scroll::-webkit-scrollbar{height:11px;width:11px}
.scroll::-webkit-scrollbar-thumb{background:var(--line2);border-radius:6px;border:3px solid var(--bg)}
.scroll::-webkit-scrollbar-thumb:hover{background:var(--faint)}
@media(max-width:720px){
  .strip{overflow-x:auto}.claninfo{display:none}header{padding:12px 16px}
  .controls{padding:10px 16px;gap:10px}
  .controls .cgroup{min-width:0;overflow:hidden}
  #sortSeg{overflow-x:auto;-webkit-overflow-scrolling:touch}
}
@media(max-width:560px){
  th.pcorner,td.pcol{width:118px;min-width:118px}th.pcorner{padding:8px 10px}td.pcol{padding:7px 10px}
  th.pcorner .s{display:none}th.mcorner,td.mcol{left:118px;width:40px;min-width:40px}th.mcorner .s{display:none}
  .pname{font-size:13px}.pw .wlbl{display:none}.pmeta{gap:5px}
  th.wh,td.cell{width:72px;min-width:72px}th.wh{padding:7px 4px 8px}
  .legend{display:none}
}
</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="crest">B</div>
    <div>
      <h1>Buzzzzz War Tracker</h1>
      <div class="sub mono" id="subline"></div>
    </div>
  </div>
  <div class="htools">
    <div class="claninfo">
      <div><b id="memCount">—</b> · <span id="warCount">—</span></div>
      <div id="windowLine"></div>
      <div id="schedLine" style="font-size:11px;color:var(--faint);margin-top:1px"></div>
    </div>
  </div>
</header>
<section class="strip" id="strip"></section>
<div class="controls">
  <div class="cgroup"><span class="clab">Show</span>
    <div class="seg" id="filterSeg">
      <button data-f="active" aria-pressed="true">Active</button>
      <button data-f="all">Everyone</button>
      <button data-f="left">Left clan</button>
    </div>
  </div>
  <div class="cgroup"><span class="clab">Sort</span>
    <div class="seg" id="sortSeg">
      <button data-s="th" aria-pressed="true">TH Level</button>
      <button data-s="participation">Participation</button>
      <button data-s="missed">Most Missed</button>
      <button data-s="delta">TH &#916;</button>
      <button data-s="name">A–Z</button>
    </div>
  </div>
  <div class="cgroup"><span class="clab">Cells</span>
    <div class="seg" id="viewSeg">
      <button data-v="stars" aria-pressed="true">Stars</button>
      <button data-v="delta">TH &#916;</button>
      <button data-v="full">Detail</button>
    </div>
  </div>
  <div class="spacer"></div>
  <div class="legend">
    <span class="leg"><span class="swatch full"></span>Both used</span>
    <span class="leg"><span class="swatch part"></span>1 of 2</span>
    <span class="leg"><span class="swatch miss"></span>Missed</span>
    <span class="leg"><span class="swatch none"></span>Not in war</span>
    <span class="leg" style="margin-left:4px"><span class="dch up" style="margin:0">&#9650;</span>Hit up</span>
    <span class="leg"><span class="dch dip" style="margin:0">&#9660;</span>Hit down</span>
    <span class="leg"><span class="clean" style="margin:0">&#8635;</span>Cleanup</span>
  </div>
  <div class="cgroup" style="gap:5px">
    <button class="scrbtn" id="scrollL" aria-label="Newer wars" disabled>
      <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11.5 3.5L6 9l5.5 5.5"/></svg>
    </button>
    <button class="scrbtn" id="scrollR" aria-label="Older wars">
      <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 3.5L12 9l-5.5 5.5"/></svg>
    </button>
  </div>
</div>
<div class="matrix">
  <div class="scroll">
    <table id="grid"><thead id="thead"></thead><tbody id="tbody"></tbody></table>
  </div>
</div>
<script>
window.WARDATA=__WARDATA_JSON__;
(function(){
  const D=window.WARDATA;
  D.filterMembers=function(list,key){
    if(key==='all')return list.slice();
    if(key==='left')return list.filter(m=>m.status==='left');
    return list.filter(m=>m.status==='active');
  };
  D.sortMembers=function(list,key,warId){
    const o=list.slice();
    switch(key){
      case'th':o.sort((a,b)=>{
        if(a.th>0&&b.th>0)return b.th-a.th||(a.thRank||999)-(b.thRank||999);
        if(a.th>0)return -1;if(b.th>0)return 1;
        return(a.thRank||999)-(b.thRank||999)||sortName(a.name).localeCompare(sortName(b.name));
      });break;
      case'participation':o.sort((a,b)=>b.played-a.played||sortName(a.name).localeCompare(sortName(b.name)));break;
      case'missed':o.sort((a,b)=>b.missed-a.missed||b.available-a.available||sortName(a.name).localeCompare(sortName(b.name)));break;
      case'delta':o.sort((a,b)=>b.avgDelta-a.avgDelta||sortName(a.name).localeCompare(sortName(b.name)));break;
      case'name':o.sort((a,b)=>sortName(a.name).localeCompare(sortName(b.name)));break;
      case'warfocus':o.sort((a,b)=>{
        const ca=a.cells[warId]||null, cb=b.cells[warId]||null;
        const rank=c=>{if(!c)return 0;if(c.pending)return 1;if(c.used===0)return 2;return 3;};
        const ra=rank(ca),rb=rank(cb);
        if(ra!==rb)return rb-ra;
        if(ra===3)return(cb.stars||0)-(ca.stars||0);
        return sortName(a.name).localeCompare(sortName(b.name));
      });break;
      default:o.sort((a,b)=>{
        if(a.th>0&&b.th>0)return b.th-a.th||(a.thRank||999)-(b.thRank||999);
        if(a.th>0)return -1;if(b.th>0)return 1;
        return(a.thRank||999)-(b.thRank||999)||sortName(a.name).localeCompare(sortName(b.name));
      });
    }
    return o;
  };
  D.summary=function(list){
    const n=list.length||1;
    return{
      count:list.length,
      totalMissed:list.reduce((s,m)=>s+m.missed,0),
      avgParticipation:list.reduce((s,m)=>s+m.participation,0)/n,
      cleanCount:list.filter(m=>m.missed===0).length,
      warsInWindow:D.wars.filter(w=>w.inWindow&&!w.pending).length,
      sumDelta:list.reduce((s,m)=>s+m.sumDelta,0),
      atkCount:list.reduce((s,m)=>s+m.atkCount,0),
      dips:list.reduce((s,m)=>s+m.dips,0),
      reaches:list.reduce((s,m)=>s+m.reaches,0),
      rawStars:list.reduce((s,m)=>s+m.rawStars,0),
      netStars:list.reduce((s,m)=>s+m.netStars,0),
      v2Wars:D.wars.filter(w=>w.v2&&w.inWindow&&!w.pending).length,
      get avgDelta(){return this.atkCount?this.sumDelta/this.atkCount:0;}
    };
  };
})();
</script>
<script>
function stripEmoji(s){return s.replace(/[^\x20-\x7E\xC0-ɏ]+/g,'').trim();}
function sortName(n){return stripEmoji(n);}
(function(){
  const D=window.WARDATA;
  const state={filter:'active',sort:'th',view:'stars',warFocus:null};
  const pct=x=>Math.round(x*100)+'%';
  const RES={win:'WIN',loss:'LOSS',draw:'DRAW',live:'LIVE'};
  function heat(n){return n===0?'h0':(n<=2?'h1':(n<=4?'h2':'h3'));}
  function renderStrip(list){
    const s=D.summary(list);
    const items=[
      {k:'Wars fully missed',v:s.totalMissed,u:(s.count-s.cleanCount)+' member'+(s.count-s.cleanCount!==1?'s':'')+' affected',alert:s.totalMissed>0,c:'var(--miss-tx)'},
      {k:'Avg attack Δ',v:(s.avgDelta>=0?'+':'−')+Math.abs(s.avgDelta).toFixed(1),u:s.dips+' dips · '+s.reaches+' reaches · excl. CWL',c:s.avgDelta<0?'var(--dip-tx)':'var(--reach-tx)'},
    ];
    document.getElementById('strip').innerHTML=items.map(it=>
      '<div class="kpi'+(it.alert?' alert':'')+'"><div class="k"><span class="pelt" style="background:'+it.c+'"></span>'+it.k+'</div>'+
      '<div class="v mono">'+it.v+'</div><div class="u">'+it.u+'</div></div>'
    ).join('');
  }
  // Find first archived (out-of-window) war index for visual separator
  const arcStartIdx=D.wars.findIndex(w=>!w.inWindow&&!w.pending);
  function renderHead(){
    let h='<tr><th class="pcorner"><div class="t">Player</div><div class="s">Participation excl. CWL</div></th>'+
           '<th class="mcorner"><div class="t">Missed</div><div class="s">60 days</div></th>';
    D.wars.forEach((w,i)=>{
      const arcCls=(i===arcStartIdx)?' arc-start':'';
      h+='<th class="wh'+(w.cwl?' iscwl':'')+(w.inWindow?'':' archived')+arcCls+'" data-wid="'+w.id+'">' +
        '<div class="whrow"><span class="wdate">'+w.date+'</span>' +
        (w.cwl?'<span class="cwl">CWL</span>':'')+
        (w.v2?'<span class="v2dot" title="v2 — TH levels + net stars"></span>':'')+'</div>'+
        '<div class="wnm" title="'+w.name+'">'+w.name+'</div>'+
        '<div class="wmeta"><span class="wsz">'+w.size+'</span><span class="wres '+w.result+'">'+RES[w.result]+'</span></div>'+
      '</th>';
    });
    document.getElementById('thead').innerHTML=h+'</tr>';
  }
  function dCls(d){return d>0?'up':(d<0?'dip':'even');}
  function dTxt(d){return d>0?'+'+d:(d<0?'−'+Math.abs(d):'=0');}
  function dArrow(d){return d>0?'▲':(d<0?'▼':'=');}
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function cellHtml(w,c){
    const arcCls=(D.wars.indexOf(w)===arcStartIdx)?' arc-start':'';
    if(c==null)return'<td class="cell none'+arcCls+'"><span class="dash">·</span></td>';
    if(c.pending)return'<td class="cell live'+arcCls+'"><span class="lv">PENDING</span></td>';
    const archivedCls=w.inWindow?'':' archived';
    const cwlCls=w.cwl?' iscwl':'';
    if(c.used===0){
      return'<td class="cell miss'+cwlCls+archivedCls+arcCls+'" title="'+esc(w.name)+' — missed '+c.max+' attack'+(c.max>1?'s':'')+'">' +
        '<div class="cmain"><span class="ua">0/'+c.max+'</span><span class="mx">miss</span></div>'+
        '<div class="cdelta"></div><div class="cd">no attacks used</div></td>';
    }
    const cls=c.used<c.max?'part':'full';
    const overlap=c.v2&&c.rawStars>c.stars;
    const starHtml='<span class="st">'+c.stars+'★</span>'+(overlap?'<span class="clean" title="'+c.rawStars+'★ raw → '+c.stars+'★ net">↻</span>':'');
    const chips=c.v2
      ?c.attacks.map(a=>'<span class="dch '+dCls(a.delta)+'">'+dArrow(a.delta)+(a.delta?dTxt(a.delta):'')+' </span>').join('')
      :'<span class="dch na">no TH</span>';
    const dets=c.attacks.map(a=>{
      if(c.v2){
        const newTxt=a.neu===0?'<span class="zero">0 new</span>':(a.neu+'★ new');
        const rawNote=a.raw>a.neu?' <span class="raw">of '+a.raw+'</span>':'';
        return'#'+c.pos+' <span class="ato">›</span> #'+a.to+' vs TH'+a.defTh+' · '+newTxt+rawNote;
      }
      return'#'+c.pos+' <span class="ato">›</span> #'+a.to+' · '+a.raw+'★';
    }).join('<br>');
    const title=c.v2
      ?esc(w.name)+' (v2) — '+c.used+'/'+c.max+' · '+c.stars+'★ net/'+c.rawStars+'★ raw'
      :esc(w.name)+' (v1) — '+c.used+'/'+c.max+' · '+c.rawStars+'★';
    return'<td class="cell '+cls+cwlCls+archivedCls+arcCls+(overlap?' hasclean':'')+'" title="'+title+'">' +
      '<div class="cmain"><span class="ua">'+c.used+'/'+c.max+'</span>'+starHtml+'</div>'+
      '<div class="cdelta">'+chips+'</div>'+
      '<div class="cd">'+dets+'</div></td>';
  }
  function renderBody(list){
    document.getElementById('tbody').innerHTML=list.map(m=>{
      let r='<tr>';
      r+='<td class="pcol"><div class="pname" title="'+esc(m.name)+'">'+esc(stripEmoji(m.name))+'</div>'+
        '<div class="pmeta"><span class="badge '+m.status+'">'+(m.status==='left'?'Left':'Active')+'</span>'+
        (m.status==='active'&&m.th?'<span class="thbadge">TH'+m.th+'</span>':'')+
        (m.status==='active'?'<span class="pw">'+m.played+'/'+m.eligible+' <span class="wlbl">wars</span></span>':'')+
        '</div></td>';
      r+='<td class="mcol"><span class="mval mono '+heat(m.missed)+'">'+m.missed+'</span></td>';
      D.wars.forEach(w=>{r+=cellHtml(w,m.cells[w.id]||null);});
      return r+'</tr>';
    }).join('');
  }
  function render(){
    let list=D.filterMembers(D.members,state.filter);
    list=state.warFocus?D.sortMembers(list,'warfocus',state.warFocus):D.sortMembers(list,state.sort);
    renderStrip(list);
    renderBody(list);
    const g=document.getElementById('grid');
    g.classList.remove('view-stars','view-delta','view-full');
    g.classList.add('view-'+state.view);
    document.querySelectorAll('th.wh').forEach(th=>th.classList.toggle('focused',th.dataset.wid===state.warFocus));
    const sub=document.querySelector('th.pcorner .s');
    if(sub)sub.textContent=state.warFocus?'Click war again to clear':'Participation excl. CWL';
  }
  function wireSeg(id,key,attr,onchange){
    const seg=document.getElementById(id);
    seg.addEventListener('click',e=>{
      const b=e.target.closest('button');if(!b)return;
      state[key]=b.dataset[attr];
      [...seg.children].forEach(c=>c.setAttribute('aria-pressed',c===b));
      if(onchange)onchange();
      render();
    });
  }
  const meta=D.meta;
  document.getElementById('subline').textContent=meta.clanTag+' · Rolling '+meta.windowDays+'-day window';
  (function showSchedule(){
    const UTC_HOURS=[0,4,8,12,16,20];
    const RUNNER_LAG=7*60*1000; // ~7 min: cron trigger → API fetch → commit → Netlify deploy
    const now=new Date();
    const nowUTC=now.getUTCHours()*60+now.getUTCMinutes();
    const nextH=UTC_HOURS.find(h=>h*60>nowUTC)??UTC_HOURS[0];
    let cronNext=new Date(Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate(),nextH,0,0));
    if(cronNext<=now)cronNext.setUTCDate(cronNext.getUTCDate()+1);
    // If war is ending before next cron, use that time instead
    const warEndISO=meta.warEndISO||'';
    let est=new Date(cronNext.getTime()+RUNNER_LAG);
    if(warEndISO){
      const warEnd=new Date(warEndISO);
      const smartEst=new Date(warEnd.getTime()+3*60*1000+RUNNER_LAG);
      if(smartEst>now&&smartEst<est)est=smartEst;
    }
    const el=document.getElementById('schedLine');
    if(el)el.textContent='Est. next update: '+est.toLocaleTimeString([],{hour:'numeric',minute:'2-digit'});
  })();
  document.getElementById('memCount').textContent=D.members.filter(m=>m.status==='active').length+' active';
  document.getElementById('warCount').textContent=D.wars.filter(w=>w.inWindow&&!w.pending).length+' wars in window';
  document.getElementById('windowLine').textContent=meta.windowLabel;
  wireSeg('filterSeg','filter','f');
  wireSeg('sortSeg','sort','s',()=>{state.warFocus=null;});
  wireSeg('viewSeg','view','v');
  renderHead();
  document.getElementById('thead').addEventListener('click',e=>{
    const th=e.target.closest('th.wh');if(!th)return;
    const wid=th.dataset.wid;
    state.warFocus=(state.warFocus===wid)?null:wid;
    render();
  });
  (function normalizeColWidths(){
    const ths=[...document.querySelectorAll('th.wh')];
    if(!ths.length)return;
    ths.forEach(th=>{th.style.width='max-content';});
    const maxW=Math.ceil(Math.max(...ths.map(th=>th.offsetWidth)));
    ths.forEach(th=>{th.style.width='';});
    document.documentElement.style.setProperty('--warcol-w',maxW+'px');
  })();
  render();
  const scrollEl=document.querySelector('.scroll');
  const btnL=document.getElementById('scrollL');
  const btnR=document.getElementById('scrollR');
  function updateNav(){
    const maxL=scrollEl.scrollWidth-scrollEl.clientWidth;
    const noOverflow=maxL<=4;
    btnL.style.display=noOverflow?'none':'';
    btnR.style.display=noOverflow?'none':'';
    btnL.disabled=scrollEl.scrollLeft<=4;
    btnR.disabled=scrollEl.scrollLeft>=maxL-4;
  }
  function pageScroll(dir){scrollEl.scrollBy({left:dir*Math.max(240,scrollEl.clientWidth-290),behavior:'smooth'});}
  btnL.addEventListener('click',()=>pageScroll(-1));
  btnR.addEventListener('click',()=>pageScroll(1));
  scrollEl.addEventListener('scroll',updateNav,{passive:true});
  window.addEventListener('resize',updateNav);
  window.addEventListener('keydown',e=>{
    if(e.target.closest&&e.target.closest('input,[contenteditable]'))return;
    if(e.key==='ArrowRight')pageScroll(1);
    else if(e.key==='ArrowLeft')pageScroll(-1);
  });
  updateNav();
})();
</script>
</body>
</html>"""

html = _HTML.replace('__WARDATA_JSON__', _wardata_json)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Written: {out}")
print(f"Size: {os.path.getsize(out):,} bytes")
