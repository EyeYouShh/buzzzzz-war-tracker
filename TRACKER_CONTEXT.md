# Buzzzzz War Tracker — Context & Maintenance Guide

**Last updated:** June 2026 (session 2)  
**Live site:** Netlify auto-deploy from GitHub (EyeYouShh/buzzzzz-war-tracker)  
**Clan:** Buzzzzz `#2GGL80JL0` · CoC API + Oracle VM runner

---

## Architecture Overview

```
build_tracker.py   ← Source of truth. All WAR_BLOCKS, PLAYERS, config.
update_tracker.py  ← Runner: fetches API, updates build_tracker.py, regenerates HTML.
index.html         ← Generated output (war tracker). Never edit directly.
cwl.html           ← Generated output (CWL tracker). Never edit directly.
TRACKER_CONTEXT.md ← This file.

data/
  scraped_cwl.json         ← 42 CWL entries (Dec 2025 – May 2026), full v2 format
  scraped_wars.json        ← 57 regular war metadata (Nov 2025 – May 2026)
  scraped_wars_v2.json     ← 57 regular wars with full v2 block data

scripts/
  import_wars.py           ← One-time: imported CWL v2 data into build_tracker.py
  import_regular_wars.py   ← One-time: imported regular war v2 data
  scrape_cwl.py            ← One-time: scraped CWL pages via ClashSpot fetch
```

**Pipeline:**
`update_tracker.py` (GitHub Actions, every 4h) → updates `build_tracker.py` → regenerates `index.html` + `cwl.html` → git push → Netlify auto-deploys.

---

## Data Format — WAR_BLOCK

Every war is one tuple in the `WAR_BLOCKS` list. Newest first.

### V2 format (current — all wars from Nov 2025+)
```python
("WAR_ID", "M/D/YY", "Opponent Name", "NvN", """
#PLAYERTAG|name|warPos|TH|attacksUsed|totalRawStars|totalNetStars|defPos:rawStars:netStars:defTH,...
...
"""),                         # regular war (completed)
("ID", ..., ..., ..., """\n...\n""", True),         # in-progress regular war
("ID", ..., ..., ..., """\n...\n""", False, True),  # completed CWL war
("ID", ..., ..., ..., """\n...\n""", True, True),   # in-progress CWL war
```

**Net stars** = contribution above previous best on that base. Tracks real damage dealt.  
**TH delta** = defenderTH − attackerTH (positive = hitting up, negative = hitting down).

### V1 format (legacy — pre-Nov 2025 wars, untouched)
```python
name|warPos|attacksUsed|totalStars|defPos:stars,...
```
V1 has no tags, no TH levels, no net star distinction. Still renders fine (falls back gracefully).

### WAR_BLOCK IDs
- **Regular wars**: numeric (e.g. `273131437`) — from `startTime` digits via `war_id_from_start()`
- **CWL wars**: alphanumeric (e.g. `8Q0J0022Q`) — CoC API's native `warTag`

---

## Key Data Structures in build_tracker.py

### `ACTIVE` set
Names of current clan members. **Auto-updated by `update_tracker.py`** on every runner cycle (compares against `/clans/{tag}/members` API endpoint).

### `PLAYER_TH` dict
`name → TH level`. **Auto-updated by runner** when TH changes are detected. Used as fallback when API TH isn't in war data.

### `PLAYER_TAGS` dict
`"#TAG" → "name"`. **Auto-updated by runner** from war data. Enables deduplication between v1 (name-keyed) and v2 (tag-keyed) war entries. Placeholder entry `"#XXXXXXXX": "DisplayName"` is intentional (ignored by code).

### `_CS_ORDER` list
Manual tiebreaker ordering within same TH tier (matches in-game display order). New members auto-assigned rank 999 (sort to end of their TH group). Update manually when fine ordering matters.

### `RESULTS` dict
`"WAR_ID" → "W"/"L"/"D"`. Populated automatically by runner for newly-ended wars. Historical wars manually set.

### `WAR_END_ISO`
ISO timestamp of active war's end time. Set by runner during `inWar` state so JS can show smart "Next update" time instead of next cron slot. Cleared when war ends.

---

## How New Wars Get Added (Automatic)

The runner (`update_tracker.py`) runs via GitHub Actions every 4 hours:

1. **Syncs roster** — fetches `/clans/{tag}/members`, updates `ACTIVE` + `PLAYER_TH`
2. **Regular war** — fetches `/clans/{tag}/currentwar`
   - New war → prepends to `WAR_BLOCKS`
   - Existing war → updates its block (attack data refreshed)
   - Ended war → sets W/L/D in `RESULTS`
3. **CWL wars** — fetches `/clans/{tag}/currentwar/leaguegroup`, iterates all round war tags; updates both new and in-progress rounds
4. **Smart end-of-war capture** — if war ends within 4 hours, sleeps until end+3min then re-fetches final data
5. Regenerates `index.html` + `cwl.html`, commits and pushes → Netlify deploys

**Note:** The runner workflow (`update-tracker.yml`) commits `index.html`, `cwl.html`, and `build_tracker.py` on every update cycle.

---

## Manual Operations

### Adding historical wars (one-off)
1. Scrape via ClashSpot server-side fetch (see `scripts/scrape_cwl.py` for pattern)
2. Run import script (see `scripts/import_wars.py` / `scripts/import_regular_wars.py`)
3. Verify with `python3 build_tracker.py` then push

### Correcting W/L/D results
Find war ID in `RESULTS` dict, change `'W'` → `'L'` / `'D'`, rebuild and push.

### Manually adding a new regular war (v2 format)
```python
# In WAR_BLOCKS, at the top (newest first):
("WAR_ID","M/D/YY","Opponent","NvN","""
#TAG|name|pos|TH|atks|rawStars|netStars|defPos:rawStars:netStars:defTH,...
...(one line per Buzzzzz member in the war)...
"""),
# In RESULTS dict:
'WAR_ID': 'W',
```

---

## CWL Tracker (cwl.html)

Separate page linked from the main tracker's controls bar ("CWL ↗").

### How it works
- `build_tracker.py` groups all CWL wars by season (month/year) and generates `cwl.html`
- Runner updates `cwl.html` automatically every 4h alongside `index.html`
- Season dropdown (newest first): Dec 2025 → current month

### Data per season
- **Prep round detection**: `in_prog=True` AND zero attacks from all members → treated as PREP, excluded from stats
- **Missed**: only completed rounds where a rostered player used 0 attacks (live-round absences don't count)
- **Per-round `rd[]` array**: each player has `[{a, st, live}, ...]` — one slot per non-prep round, `null` = not rostered that round
- **Active members not yet placed** in any round appear at the bottom with `—` in all columns

### CWL page display
| Column | Content |
|---|---|
| R1–R7 | Per-round cells: `3★` green / `2★` gold / `1★` orange / `✕` red (missed) / `PEND` blue (live+no attack) / blank (not in round) |
| Stars | Total stars across all rounds |
| 3★·2★·1★·0★ | Attack star breakdown |
| Missed | Completed rounds where player was rostered but didn't attack |
| Avg ★ | Stars per round played |
| 8★ Reward | Full (≥8★) / Short / None / — |

### KPI strip (per season)
Record · Total ★ · Full Reward count · 3★ Rate · Avg ★/War

### Known bugs fixed
- `_replace_war_entry` had an off-by-one (`idx-1` instead of `idx`) — silently skipped ALL CWL round updates since launch. Fixed June 2026.
- `cwl.html` was missing from the runner's commit file list. Fixed June 2026.

---

## KPI Strip (top of page — War Tracker)

All KPIs computed over the **active 60-day window, regular wars only** (CWL excluded unless noted).

| KPI | Meaning |
|---|---|
| **Wars Fully Missed** | Count of wars where any member was rostered but used 0 attacks |
| **Attacked Higher TH** | % of attacks where defenderTH > attackerTH (reaching up) |
| **Attacked Same TH** | % of attacks where defenderTH = attackerTH |
| **Attacked Lower TH** | % of attacks where defenderTH < attackerTH (dipping down) |

The three TH-delta KPIs also show raw attack counts beneath the percentage.

---

## Display Features

### Rolling 60-Day Window
- Wars older than 60 days → faded archive section with a gold `|` divider
- Archived war sticky headers stay solid (not semi-transparent) for readability

### Member Rows
- **Active badge** (green) or **Left badge** (red)
- **TH badge** shown for ALL members — active shows current TH, Left shows last known TH from their final war
- Participation counter `X/Y wars` only shown for active members (excl. CWL)

### Cell Colors
| Color | Meaning |
|---|---|
| Green | Both attacks used |
| Orange | 1 of 2 attacks used |
| Red | Missed (0 attacks, was rostered) |
| Dark | Not in this war |
| Blue | War currently live |

### TH Delta View (click "TH Δ" in controls)
- Each attack shows ▲/▼/= and the numeric delta
- ▲ blue = attacking up, ▼ orange = attacking down, = faint = same TH
- ↻ icon = cleanup attack (defender had stars already; net < raw)

### Sort Options
- **TH Level** — by current TH desc, then in-game order within tier
- **Participation** — most wars played first
- **Most Missed** — worst attenders first
- **TH Δ** — best avg TH delta first
- **A–Z** — alphabetical
- **War focus** — clicking a war column header sorts by performance in that war

---

## Infrastructure

| Component | Details |
|---|---|
| **GitHub repo** | EyeYouShh/buzzzzz-war-tracker |
| **Netlify site** | Auto-deploys on every push to main |
| **Runner host** | Oracle Cloud VM · IP: `129.159.175.24` (static) |
| **Runner script** | `/home/opc/update_tracker.py` (or via GitHub Actions) |
| **API key** | In `COC_API_KEY` GitHub Secret — **never in code** |
| **Cron schedule** | Every 4 hours at UTC 0, 4, 8, 12, 16, 20 |

### Security
`COC_API_KEY` is a GitHub Actions Secret only. Never stored in code, logs, or this doc.  
CoC API key is IP-locked to `129.159.175.24`.

---

## Historical Coverage

| Period | Type | Count | Format | Source |
|---|---|---|---|---|
| Jun 2026 | Regular + CWL | Live (auto-updated) | v2 API | CoC API |
| May 2026 | Regular + CWL | ~14 wars | v2 API | CoC API |
| Apr 2026 | Regular + CWL | ~16 wars | v2 | ClashSpot scrape |
| Mar 2026 | Regular + CWL | ~15 wars | v2 | ClashSpot scrape |
| Jan–Feb 2026 | Regular + CWL | ~25 wars | v2 | ClashSpot scrape |
| Dec 2025 | Regular + CWL | ~15 wars | v2 | ClashSpot scrape |
| Nov 2025 | Regular | ~8 wars | v2 | ClashSpot scrape |
| Pre-Nov 2025 | Regular | ~8 wars | v1 | Manual entry |

**Total: 102 wars tracked, 199 unique players, 41 currently active.**

---

## ClashSpot Scraping Notes (for future historical imports)

ClashSpot renders war member data in **static HTML** (server-side rendered), enabling bulk fetch:

```javascript
// Fetch a war page and parse it without navigation:
const html = await (await fetch('https://clashspot.net/en/clan/2GGL80JL0/war/WAR_ID')).text();
const doc = new DOMParser().parseFromString(html, 'text/html');
// Extract .members-position elements
// Use getAttribute('href') and getAttribute('title') (not .href/.title — different in non-rendered docs)
```

**CWL URLs** on ClashSpot are NOT accessible via standard `/clan/ID/war/ID` — they require league-group-specific URLs and are JS-rendered only. CWL data must come from CoC API.

**Cloudflare protection**: Opening many ClashSpot tabs simultaneously triggers bot detection. Solve CAPTCHA once; clearance cookie persists for all same-origin tabs.

---

## Clan Info

- **Clan tag**: `#2GGL80JL0`
- **ClashSpot**: `https://clashspot.net/en/clan/2GGL80JL0/`
- **60-day kick threshold**: 5 wars missed in 60 days
- **War size**: 30v30 standard
- **CWL**: participates monthly, 7 rounds per season
