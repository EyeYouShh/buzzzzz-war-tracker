import json, re, os

# ===== ACTIVE MEMBERS (current roster) =====
ACTIVE = {
    # Current 42-member roster (verified May 29, 2026 from ClashSpot)
    # Removed: Aldich, Dohtem, OOLIJ, Redstone Copper, atlas
    "gen","stage6yo","Slayer","Gr8Conqueror","wato","Americanpatriot","drybonez",
    "crimpo","SwiftyKinja","Big Steppa","rour","Jac","Cole","stage5yo","studkiller","arius67'",
    "DE1","Kizaru","MiniPekka","UNSTOPPABLE ADI","Ste","Pam from HR","Sumairu","Marrow",
    "⚡️LSWreckless⚡️","uhlisuh","SurgeGold","MR. ASURAN YT","SWAGMUFFIN90",
    "Pharah","Brandon","Loading…","Stevie Wonder","jj","DandyPickle","F16","Tretor",
    "rinz","das","seth","Mr.Minzy kipz","Halid #1"
}

# ===== RAW WAR DATA (newest first) =====
WAR_BLOCKS = [
("273131437","5/29/26","Friendj of wer","30v30","""Slayer|1|0|0|
Gr8Conqueror|2|0|0|
stage6yo|3|0|0|
wato|4|0|0|
Big Steppa|5|0|0|
Americanpatriot|6|0|0|
stage5yo|7|0|0|
DE1|8|0|0|
SwiftyKinja|9|0|0|
Jac|10|0|0|
crimpo|11|0|0|
studkiller|12|0|0|
MiniPekka|13|0|0|
Cole|14|0|0|
Kizaru|15|0|0|
Pam from HR|16|0|0|
Halid #1|17|0|0|
Loading…|18|0|0|
arius67'|19|0|0|
MR. ASURAN YT|20|0|0|
Ste|21|0|0|
SWAGMUFFIN90|22|0|0|
uhlisuh|23|0|0|
Marrow|24|0|0|
jj|25|0|0|
UNSTOPPABLE ADI|26|0|0|
Stevie Wonder|27|0|0|
das|28|0|0|
rinz|29|0|0|
Tretor|30|0|0|""", True),

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
    # CWL — Buzzzzz 1st in both seasons
    '8Q0J0022Q': 'W', '8Q0G02CGY': 'W', '8Q0L0VR82': 'W', '8Q0P0CYLR': 'W',
    '8Q0882R82': 'W', '8Q0020RCC': 'W', '8LVUPY0R9': 'W',
    '8LGRLVYU9': 'W', '8LGQYCQQ2': 'W', '8LGY9RLGQ': 'W', '8LG98L2PC': 'W',
    '8LG0VRGUQ': 'W', '8LQUVPLJ9': 'W', '8LQCG02G9': 'W',
}

def parse_war(war_id, date, opp, size, raw, in_prog=False, cwl=False):
    players = {}
    for line in raw.strip().split('\n'):
        parts = line.split('|')
        if len(parts) < 4:
            continue
        name = parts[0]
        pos = int(parts[1])
        atks = int(parts[2])
        stars = int(parts[3])
        atk_detail = []
        if len(parts) > 4 and parts[4]:
            for pair in parts[4].split(','):
                if ':' in pair:
                    tp, st = pair.split(':')
                    atk_detail.append([tp, int(st)])
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

# Seed all_players from ACTIVE first so every current member always gets a row
all_players = {}
for name in ACTIVE:
    all_players[name] = {'active': True}
# Then add anyone else seen in wars (ex-members, guests, etc.)
for w in wars:
    for name, data in w['players'].items():
        if name not in all_players:
            all_players[name] = {'active': name in ACTIVE}

# Generate JS data (missed count now calculated dynamically in JS for rolling window)
players_js = json.dumps(all_players, ensure_ascii=False)
wars_js = json.dumps(wars, ensure_ascii=False)

print(f"// Players: {len(all_players)}")
print(f"// Wars: {len(wars)}")
print("DATA OK")

html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Buzzzzz ⚔️ War Tracker</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#1e2130;color:#dde3f0;font-family:'Segoe UI',Arial,sans-serif;font-size:12px}

/* ── Header ── */
#header{background:linear-gradient(135deg,#252840 0%,#1e2130 100%);border-bottom:3px solid #f59e0b;padding:14px 20px;display:flex;align-items:center;gap:16px}
#header h1{color:#f59e0b;font-size:20px;font-weight:800;letter-spacing:0.5px;flex:1}
#header .subtitle{color:#7a8aa0;font-size:11px;white-space:nowrap}

/* ── Controls bar ── */
#controls{display:flex;gap:12px;padding:9px 16px;background:#252840;border-bottom:1px solid #323655;align-items:center;flex-wrap:wrap}
#controls label{color:#8a9ab5;font-size:11px;display:flex;align-items:center;gap:5px;font-weight:500}
#controls select{background:#1a1d2e;border:1px solid #3a3f5c;color:#dde3f0;padding:4px 10px;border-radius:6px;font-size:11px;cursor:pointer}
#controls select:focus{outline:none;border-color:#6366f1}
#window-info{font-size:10px;color:#8a9ab5;background:#1a1d2e;padding:3px 10px;border-radius:12px;border:1px solid #3a3f5c}
#stats{color:#6a7a90;font-size:10px}

/* ── Table layout ── */
.wrap{overflow:auto;max-height:calc(100vh - 97px)}
table{border-collapse:separate;border-spacing:0;white-space:nowrap;background:#252840}
th,td{border-right:1px solid #323655;border-bottom:1px solid #323655}
th:first-child,td:first-child{border-left:1px solid #323655}
thead tr:first-child th{border-top:1px solid #323655}

/* Sticky columns */
th.name-col,td.name-col{position:sticky;left:0;z-index:2;background:#252840;min-width:165px;max-width:205px;padding:6px 10px;box-shadow:3px 0 6px rgba(0,0,0,0.3)}
th.name-col{position:sticky!important;left:0!important;top:0!important;z-index:10!important;background:#1e2130!important}
th.miss-col,td.miss-col{position:sticky;right:0;z-index:2;background:#252840;text-align:center;min-width:62px;padding:4px;box-shadow:-3px 0 6px rgba(0,0,0,0.3)}
th.miss-col{position:sticky!important;right:0!important;top:0!important;z-index:10!important;background:#1e2130!important}

/* War column headers — sticky vertically */
thead tr:first-child th{position:sticky;top:0;z-index:4}
thead tr:last-child th{position:sticky;z-index:4}  /* top set by JS */
thead tr:first-child th.w-idx{background:#1e2130;color:#6a7a90;font-size:10px;font-weight:600;text-align:center;padding:4px 6px}
thead tr:first-child th.w-idx.faded{opacity:0.4}
thead tr:last-child th.war-cell{background:#252840;padding:5px 6px;text-align:center}
thead tr:last-child th.war-cell.faded{opacity:0.4}

.w-date{color:#6a7a90;font-size:10px;display:block}
.w-opp{color:#93c5fd;font-size:11px;font-weight:700;display:block;max-width:94px;overflow:hidden;text-overflow:ellipsis}
.w-size{color:#6a7a90;font-size:9px;display:block;margin-top:1px}
.cwl-tag{display:inline-block;background:#7c3aed;color:#fff;font-size:8px;font-weight:700;padding:1px 5px;border-radius:4px;margin-top:2px;letter-spacing:0.3px}
.inprog-tag{display:inline-block;background:#0ea5e9;color:#fff;font-size:8px;font-weight:700;padding:1px 5px;border-radius:4px;margin-top:2px}
.res-w{display:inline-block;background:#14532d;color:#4ade80;font-size:8px;font-weight:700;padding:1px 5px;border-radius:4px;margin-top:2px}
.res-l{display:inline-block;background:#450a0a;color:#f87171;font-size:8px;font-weight:700;padding:1px 5px;border-radius:4px;margin-top:2px}
.res-d{display:inline-block;background:#292524;color:#a8a29e;font-size:8px;font-weight:700;padding:1px 5px;border-radius:4px;margin-top:2px}

/* ── Player name column ── */
.pname{font-weight:700;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#dde3f0}
.badge{display:inline-block;font-size:9px;padding:2px 7px;border-radius:10px;margin-top:3px;font-weight:700;letter-spacing:0.2px}
.b-act{background:#14532d;color:#86efac;border:1px solid #166534}
.b-old{background:#2d2d3f;color:#6a7a90;border:1px solid #3a3f5c}
.wars-in{display:inline-block;font-size:10px;color:#94a3b8;margin-left:5px;vertical-align:middle;font-weight:500}

/* ── War cells: just two states ── */
td.war-cell{text-align:center;min-width:90px;max-width:112px;padding:4px 5px;vertical-align:top;cursor:default}
td.war-cell.c-miss,td.war-cell.c-na,td.war-cell.c-inprog{vertical-align:middle}
thead tr:last-child th.war-cell{vertical-align:bottom!important}
td.war-cell.faded{opacity:0.65}
/* Archive boundary — left edge of first out-of-window column */
th.w-idx.archive-start, th.war-cell.archive-start, td.war-cell.archive-start{
  border-left:3px solid #4a3f2a !important
}
th.w-idx.archive-start::before{
  content:'ARCHIVE';display:block;font-size:7px;color:#7a6a4a;font-weight:700;letter-spacing:0.5px;margin-bottom:2px
}

td.c-ok{background:#14532d;border-color:#166534}        /* attacked (any) – green */
td.c-miss{background:#450a0a;border-color:#7f1d1d}      /* in war, 0 attacks – red */
td.c-na{background:#1e2130;border-color:#2d3148}         /* not in war – dim */
td.c-inprog{background:#1e3a5f;border-color:#1d4ed8}    /* live/prep – blue */

.atk-main{font-size:11px;font-weight:600;color:#bbf7d0}
.atk-star{font-size:12px;color:#4ade80}
.atk-det{font-size:9px;color:#6a9a7a;margin-top:2px;line-height:1.5}
.miss-lbl{color:#f87171;font-size:11px;font-weight:700}
.na-lbl{color:#3a3f5c;font-size:13px}
.prep-lbl{color:#60a5fa;font-size:11px;font-weight:600}

/* ── Wars Missed column ── */
.miss-hdr{color:#8a9ab5;font-size:10px;font-weight:600;line-height:1.3}
.miss-num{font-size:15px;font-weight:800}
.m-ok{color:#4ade80}
.m-1{color:#facc15}
.m-2{color:#fb923c}
.m-hi{color:#f87171}

/* ── Misc ── */
tr.hidden{display:none}
tbody tr:hover td.c-ok{background:#166534}
tbody tr:hover td.c-miss{background:#7f1d1d}
tbody tr:hover td.c-na{background:#252840}
</style>
</head>
<body>
<div id="header">
  <h1>⚔️ Buzzzzz War Tracker</h1>
  <div class="subtitle" id="subtitle">Clan #2GGL80JL0 &nbsp;|&nbsp; Rolling 60-Day Window</div>
</div>
<div id="controls">
  <label>Show:
    <select id="flt">
      <option value="act">Active Members</option>
      <option value="all">Everyone</option>
      <option value="old">Left Clan</option>
    </select>
  </label>
  <label>Sort:
    <select id="srt">
      <option value="miss">Most Missed ↓</option>
      <option value="name">Name A–Z</option>
      <option value="wars">Wars Played ↓</option>
    </select>
  </label>
  <span id="window-info"></span>
  <span id="stats"></span>
  <span style="margin-left:auto;display:flex;gap:4px;align-items:center">
    <button id="scl" title="Scroll left" style="background:#1a1d2e;border:1px solid #3a3f5c;color:#8a9ab5;border-radius:6px;padding:3px 10px;cursor:pointer;font-size:14px;line-height:1">‹</button>
    <button id="scr" title="Scroll right" style="background:#1a1d2e;border:1px solid #3a3f5c;color:#8a9ab5;border-radius:6px;padding:3px 10px;cursor:pointer;font-size:14px;line-height:1">›</button>
  </span>
</div>
<div class="wrap"><table id="tbl"></table></div>
<script>
'''

html += f"const WARS={wars_js};\n"
html += f"const PLAYERS={players_js};\n"

html += r'''
// ── HTML escape helper (prevents XSS from API-sourced names) ──
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

// ── Rolling 60-day window ──
function parseWarDate(s){
  const [m,d,y]=s.split('/').map(Number);
  return new Date(2000+y,m-1,d);
}
const today=new Date();
const cutoff=new Date(today);
cutoff.setDate(today.getDate()-60);

function inWindow(w){ return parseWarDate(w.date)>=cutoff; }

// Set window info label
const fmtDate=d=>d.toLocaleDateString('en-US',{month:'short',day:'numeric'});
document.getElementById('window-info').textContent=
  `60-day window: ${fmtDate(cutoff)} – ${fmtDate(today)}`;

// ── Helpers ──
function calcMissed(name){
  return WARS.filter(w=>
    !w.in_prog && inWindow(w) &&
    w.players[name] &&
    w.players[name].p>0 &&
    w.players[name].a===0
  ).length;
}

function atkDetail(ppos,atks){
  return atks.map(([tp,st])=>`#${ppos}→#${tp}: ${st}★`).join('<br>');
}

function maxAtks(w){ return w.cwl ? 1 : 2; }

function resultBadge(w){
  if(w.in_prog) return '<span class="inprog-tag">LIVE</span>';
  if(w.result==='W') return '<span class="res-w">WIN</span>';
  if(w.result==='L') return '<span class="res-l">LOSS</span>';
  if(w.result==='D') return '<span class="res-d">DRAW</span>';
  return '';
}

// Wars In stat logic:
// - If player ever appeared in ANY war in the full archive (even outside 60-day window)
//   → they're a veteran; denominator = all in-window non-CWL wars
// - If first appearance is within the window → they're new;
//   denominator = in-window wars from their first appearance onwards
// Participation includes in-progress wars (rostered = participating)
// Only Missed excludes in-prog (battle not over yet)
const eligibleWars = WARS.filter(w=>!w.cwl&&inWindow(w));
const eligibleCount = eligibleWars.length;

function getWarsInStat(name){
  // Find very first appearance across ALL archived wars (oldest-first scan)
  const allRegular = WARS.filter(w=>!w.cwl);
  // allRegular is newest-first, so last element = oldest war
  const firstEver = allRegular.slice().reverse().find(w=>w.players[name]);
  if(!firstEver) return {inn:0, tot:0};

  const firstDate = parseWarDate(firstEver.date);
  let tot;
  if(firstDate < cutoff){
    // Veteran — was here before the window opened
    tot = eligibleCount;
  } else {
    // New member — count in-window wars from their first appearance (newest-first array)
    // Find the last index in eligibleWars (oldest) where they appear
    let lastIdx = -1;
    for(let i=eligibleWars.length-1;i>=0;i--){
      if(eligibleWars[i].players[name]){lastIdx=i;break;}
    }
    tot = lastIdx===-1 ? 0 : lastIdx+1;
  }
  const inn = eligibleWars.filter(w=>w.players[name]).length;
  return {inn, tot};
}

// ── Build table ──
function buildTable(){
  const flt=document.getElementById('flt').value;
  const srt=document.getElementById('srt').value;

  let players=Object.keys(PLAYERS).filter(n=>{
    if(flt==='act') return PLAYERS[n].active;
    if(flt==='old') return !PLAYERS[n].active;
    return true;
  });

  // Pre-compute missed (rolling 60-day window)
  const missedMap={};
  players.forEach(n=>{ missedMap[n]=calcMissed(n); });

  if(srt==='miss') players.sort((a,b)=>{
    const dm=missedMap[b]-missedMap[a];
    return dm!==0?dm:a.localeCompare(b);
  });
  else if(srt==='name') players.sort((a,b)=>a.localeCompare(b));
  else if(srt==='wars') players.sort((a,b)=>{
    const aw=getWarsInStat(a).inn;
    const bw=getWarsInStat(b).inn;
    return bw-aw||a.localeCompare(b);
  });

  const tbl=document.getElementById('tbl');
  let h='<thead>';

  // Find index of first archive (out-of-window) war
  const archiveStartIdx = WARS.findIndex(w=>!inWindow(w));

  // Row 1: W1, W2… labels
  h+='<tr><th class="name-col" rowspan="2" style="vertical-align:bottom;font-size:11px;color:#8a9ab5">Player<br><span style="font-size:9px;color:#7a8aa0;font-weight:400">War Participation Excludes CWL</span></th>';
  WARS.forEach((w,i)=>{
    const inW=inWindow(w);
    const fd=inW?'':' faded';
    const arc=(!inW&&i===archiveStartIdx)?' archive-start':'';
    h+=`<th class="w-idx${fd}${arc}">W${i+1}</th>`;
  });
  h+='<th class="miss-col" rowspan="2" style="vertical-align:middle"><span class="miss-hdr">Missed<br><span style="font-size:9px;color:#94a3b8">(60 days)</span></span></th></tr>';

  // Row 2: war details
  h+='<tr>';
  WARS.forEach((w,i)=>{
    const inW=inWindow(w);
    const fd=inW?'':' faded';
    const arc=(!inW&&i===archiveStartIdx)?' archive-start':'';
    const cwlBadge=w.cwl?'<span class="cwl-tag">CWL</span>':'';
    h+=`<th class="war-cell${fd}${arc}"><span class="w-date">${w.date}</span><span class="w-opp" title="${esc(w.opp)}">${esc(w.opp)}</span><span class="w-size">${w.size}</span>${cwlBadge}${resultBadge(w)}</th>`;
  });
  h+='</tr></thead>';

  h+='<tbody>';
  let shown=0, activeShown=0;
  players.forEach(name=>{
    const pd=PLAYERS[name];
    const mc=missedMap[name];
    shown++;
    if(pd.active) activeShown++;
    h+=`<tr>`;
    const badge=pd.active
      ?'<span class="badge b-act">Active</span>'
      :'<span class="badge b-old">Left</span>';
    const {inn,tot}=getWarsInStat(name);
    const wiStr=(pd.active&&tot>0)?`<span class="wars-in">${inn}/${tot} wars</span>`:'';
    h+=`<td class="name-col"><div class="pname" title="${esc(name)}">${esc(name)}</div>${badge} ${wiStr}</td>`;

    WARS.forEach((w,wi)=>{
      const wp=w.players[name];
      const inW=inWindow(w);
      const fd=inW?'':' faded';
      const arc=(!inW&&wi===archiveStartIdx)?' archive-start':'';
      const ma=maxAtks(w);
      if(!wp){
        h+=`<td class="war-cell c-na${fd}${arc}"><span class="na-lbl">—</span></td>`;
      } else if(wp.a===0){
        if(w.in_prog){
          h+=`<td class="war-cell c-inprog${fd}${arc}" title="War in progress"><span class="prep-lbl">⏳ Pending</span></td>`;
        } else {
          h+=`<td class="war-cell c-miss${fd}${arc}" title="In war, 0 attacks used"><span class="miss-lbl">💀 0 atk</span></td>`;
        }
      } else {
        const det=atkDetail(wp.p, wp.atks);
        h+=`<td class="war-cell c-ok${fd}${arc}" title="${det.replace(/<br>/g,'\n')}">`;
        h+=`<div class="atk-main">${wp.a}/${ma} <span class="atk-star">${wp.s}★</span></div>`;
        h+=`<div class="atk-det">${det}</div>`;
        h+=`</td>`;
      }
    });

    // Missed count
    const mcls=mc===0?'m-ok':mc===1?'m-1':mc<=3?'m-2':'m-hi';
    h+=`<td class="miss-col"><span class="miss-num ${mcls}">${mc}</span></td>`;
    h+='</tr>';
  });
  h+='</tbody>';
  tbl.innerHTML=h;

  // Pin second header row directly below first
  const row1=document.querySelector('thead tr:first-child');
  if(row1){
    const h1=row1.offsetHeight;
    document.querySelectorAll('thead tr:last-child th').forEach(th=>th.style.top=h1+'px');
  }

  const wInWindow=WARS.filter(inWindow).length;
  document.getElementById('stats').textContent=
    `${shown} members · ${wInWindow} wars in window`;
}

document.getElementById('flt').addEventListener('change',buildTable);
document.getElementById('srt').addEventListener('change',buildTable);
buildTable();

// Scroll controls
(function(){
  const wrap=document.querySelector('.wrap');
  let timer=null;
  function scroll(dir){wrap.scrollBy({left:dir*220,behavior:'smooth'});}
  function startScroll(dir){
    scroll(dir);
    timer=setInterval(()=>wrap.scrollBy({left:dir*120,behavior:'auto'}),120);
  }
  function stopScroll(){clearInterval(timer);timer=null;}
  ['scl','scr'].forEach((id,i)=>{
    const btn=document.getElementById(id);
    const dir=i===0?-1:1;
    btn.addEventListener('mousedown',()=>startScroll(dir));
    btn.addEventListener('touchstart',()=>startScroll(dir));
    ['mouseup','mouseleave','touchend'].forEach(e=>btn.addEventListener(e,stopScroll));
  });
})();
</script>
</body>
</html>'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buzzzzz-war-tracker.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Written: {out}")
print(f"Size: {os.path.getsize(out):,} bytes")
