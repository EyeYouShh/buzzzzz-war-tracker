#!/usr/bin/env python3
"""
Buzzzzz War Tracker — Automation Script
Fetches current war + CWL wars from CoC API and updates build_tracker.py, then regenerates HTML.
"""

import os, sys, re, json, subprocess, time
from datetime import datetime, timezone, timedelta
import urllib.request

API_KEY  = os.environ.get("COC_API_KEY", "")
CLAN_TAG = "%232GGL80JL0"   # URL-encoded #2GGL80JL0
OUR_TAG  = "#2GGL80JL0"
BASE_URL = "https://api.clashofclans.com/v1"
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
TRACKER_PY  = os.path.join(SCRIPT_DIR, "build_tracker.py")
TRACKER_HTML = os.path.join(SCRIPT_DIR, "index.html")


def api_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def war_id_from_start(start_time_str, extra=""):
    """Convert API startTime '20260529T120000.000Z' to a numeric ID string.
    Optional 'extra' suffix differentiates wars that start at the same second (e.g. CWL).
    """
    digits = re.sub(r"\D", "", start_time_str)[:14]
    base = int(digits) % 10_000_000_000
    if extra:
        # fold a stable (deterministic) hash of the extra string into the ID
        # NOTE: Python's built-in hash() is randomized per-process — use sum of ordinals instead
        h = sum(ord(c) for c in extra) % 100
        base = (base * 100 + h) % 10_000_000_000
    return str(base)


def format_war_date(start_time_str):
    """'20260529T120000.000Z' → '5/29/26'"""
    dt = datetime.strptime(start_time_str[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    return dt.strftime("%-m/%-d/%y")


def build_war_block(war_data, war_id_extra="", is_cwl=False):
    """Convert API war data to v2 WAR_BLOCK format lines.
    V2 row: #tag|name|pos|TH|atk_count|raw_stars|net_stars|defPos:rawStars:delta:defTH,...
    """
    our_clan = war_data["clan"]
    opponent = war_data["opponent"]

    def_pos = {m["tag"]: m["mapPosition"] for m in opponent.get("members", [])}
    def_th  = {m["tag"]: m.get("townHallLevel") or m.get("townhallLevel", 0) for m in opponent.get("members", [])}

    size     = war_data.get("teamSize", "?")
    war_id   = war_id_from_start(war_data["startTime"], war_id_extra)
    date     = format_war_date(war_data["startTime"])
    opp_name = opponent["name"].replace('"', '\\"').replace('\n', ' ').replace('\r', '')
    war_size = f"{size}v{size}"
    state    = war_data.get("state", "")
    in_prog  = state in ("preparation", "inWar")

    # Pass 1: collect all attacks per defender base for delta computation
    attacks_on_base = {}
    for m in our_clan.get("members", []):
        for a in m.get("attacks", []):
            dt = a["defenderTag"]
            attacks_on_base.setdefault(dt, []).append({
                "order": a.get("order", 0),
                "stars": a["stars"],
                "attackerTag": a["attackerTag"],
            })

    # Compute per-attack delta
    delta_map = {}
    for def_tag, atk_list in attacks_on_base.items():
        running_max = 0
        for atk in sorted(atk_list, key=lambda x: x["order"]):
            delta = max(0, atk["stars"] - running_max)
            delta_map[(def_tag, atk["order"])] = delta
            running_max = max(running_max, atk["stars"])

    # Pass 2: build per-member v2 rows
    rows = []
    for m in sorted(our_clan.get("members", []), key=lambda x: x["mapPosition"]):
        tag  = m["tag"]
        name = m["name"].replace('"""', '"').replace('\n', ' ').replace('\r', '').replace('|', '-')
        pos  = m["mapPosition"]
        th   = m.get("townHallLevel") or m.get("townhallLevel", 0)
        attacks   = m.get("attacks", [])
        atk_count = len(attacks)
        raw_stars = sum(a["stars"] for a in attacks)
        net_stars = sum(delta_map.get((a["defenderTag"], a.get("order", 0)), 0) for a in attacks)
        detail = ",".join(
            f"{def_pos.get(a['defenderTag'], '?')}:{a['stars']}"
            f":{delta_map.get((a['defenderTag'], a.get('order', 0)), 0)}"
            f":{def_th.get(a['defenderTag'], 0)}"
            for a in attacks
        )
        rows.append(f"{tag}|{name}|{pos}|{th}|{atk_count}|{raw_stars}|{net_stars}|{detail}")

    block_lines = "\n".join(rows)

    if in_prog and is_cwl:
        entry = f'("{war_id}","{date}","{opp_name}","{war_size}","""\n{block_lines}\n""", True, True)'
    elif in_prog:
        entry = f'("{war_id}","{date}","{opp_name}","{war_size}","""\n{block_lines}\n""", True)'
    elif is_cwl:
        entry = f'("{war_id}","{date}","{opp_name}","{war_size}","""\n{block_lines}\n""", False, True)'
    else:
        entry = f'("{war_id}","{date}","{opp_name}","{war_size}","""\n{block_lines}\n""")'

    return war_id, entry, in_prog


def update_player_tags(war_data, content):
    """Keep PLAYER_TAGS dict in build_tracker.py current."""
    members = war_data.get("clan", {}).get("members", [])
    if not members:
        return content, False

    tags_match = re.search(r'PLAYER_TAGS\s*=\s*\{([^}]*)\}', content, re.DOTALL)
    if not tags_match:
        print("WARNING: PLAYER_TAGS block not found in build_tracker.py")
        return content, False

    existing = {}
    for m in re.finditer(r'"(#[^"]+)"\s*:\s*"([^"]*)"', tags_match.group(1)):
        existing[m.group(1)] = m.group(2)

    changed = False
    for m in members:
        tag  = m["tag"]
        name = m["name"].replace('"', '\\"').replace('\n', ' ').replace('\r', '')
        if existing.get(tag) != name:
            existing[tag] = name
            changed = True

    if not changed:
        return content, False

    entries = "".join(f'    "{tag}": "{name}",\n' for tag, name in sorted(existing.items()))
    new_block = f"\n    # AUTO-UPDATED by update_tracker.py\n{entries}"
    content = content[:tags_match.start(1)] + new_block + content[tags_match.end(1):]
    print(f"Updated PLAYER_TAGS ({len(existing)} players)")
    return content, True


def update_roster(content):
    """Sync ACTIVE set and PLAYER_TH with current API clan members.

    Detects members who joined or left since last run and updates:
      - ACTIVE set  (add new joiners, remove leavers)
      - PLAYER_TH   (update current TH levels for all members)
    PLAYER_TAGS is handled separately by update_player_tags() during war processing.
    """
    try:
        data = api_get(f"/clans/{CLAN_TAG}/members")
        members = data.get("items", [])
    except Exception as e:
        print(f"Roster update: API error ({e})")
        return content, False

    if not members:
        print("Roster update: empty member list, skipping")
        return content, False

    api_names  = {m["name"] for m in members}
    api_th_map = {m["name"]: m.get("townHallLevel", 0) for m in members}

    # ── Parse current ACTIVE set ──────────────────────────────────────────────
    active_match = re.search(r'ACTIVE\s*=\s*\{([^}]*)\}', content, re.DOTALL)
    if not active_match:
        print("WARNING: Could not find ACTIVE set in build_tracker.py")
        return content, False

    current_names = set(re.findall(r'"([^"]+)"', active_match.group(1)))
    new_joiners   = sorted(api_names - current_names)
    departed      = sorted(current_names - api_names)

    roster_changed = bool(new_joiners or departed)
    if new_joiners:
        print(f"New members joined: {', '.join(new_joiners)}")
    if departed:
        print(f"Members left clan:  {', '.join(departed)}")

    if roster_changed:
        updated_names = (current_names - set(departed)) | set(new_joiners)
        today = datetime.now().strftime("%-m/%-d/%y")
        # Rebuild ACTIVE set (alphabetically sorted; user can re-order manually)
        names_str = ','.join(f'"{n}"' for n in sorted(updated_names))
        new_inner  = f'\n    # Auto-updated {today} — {len(updated_names)} members\n    {names_str}\n'
        content = content[:active_match.start(1)] + new_inner + content[active_match.end(1):]

    # ── Update PLAYER_TH levels ───────────────────────────────────────────────
    th_match = re.search(r'(PLAYER_TH\s*=\s*\{)([^}]*?)(\})', content, re.DOTALL)
    th_changed = False
    if th_match:
        th_text = th_match.group(2)
        for name, new_th in api_th_map.items():
            if new_th <= 0:
                continue
            m = re.search(r'"' + re.escape(name) + r'"\s*:\s*(\d+)', th_text)
            if m:
                old_th = int(m.group(1))
                if old_th != new_th:
                    th_text   = th_text[:m.start(1)] + str(new_th) + th_text[m.end(1):]
                    th_changed = True
                    print(f"TH upgraded: {name}  TH{old_th} → TH{new_th}")
            else:
                # New member not yet in PLAYER_TH — append
                th_text   = th_text.rstrip() + f'\n    "{name}": {new_th},\n'
                th_changed = True
                print(f"TH added: {name} TH{new_th}")
        if th_changed:
            content = content[:th_match.start(2)] + th_text + content[th_match.end(2):]

    return content, roster_changed or th_changed


def determine_result(war_data):
    our = war_data["clan"]
    opp = war_data["opponent"]
    our_stars = our.get("stars", 0)
    opp_stars = opp.get("stars", 0)
    our_dest  = our.get("destructionPercentage", 0)
    opp_dest  = opp.get("destructionPercentage", 0)
    if our_stars > opp_stars:   return "W"
    elif our_stars < opp_stars: return "L"
    elif our_dest  > opp_dest:  return "W"
    elif our_dest  < opp_dest:  return "L"
    return "D"


def _replace_war_entry(content, war_id, new_entry):
    """Safely replace a single WAR_BLOCK entry by war_id without crossing entry boundaries.

    The regex approach (.*? with DOTALL) can over-match and consume adjacent entries.
    This function instead walks the string character by character:
      1. Finds the entry opening: '("war_id",'
      2. Locates the first triple-quote  (opening of data block)
      3. Locates the second triple-quote (closing of data block)
      4. Finds the ')' that closes the tuple (may follow ', True, True' etc.)
      5. Replaces only that span — guaranteed not to cross entry boundaries.
    """
    # search_str includes the opening '(' so idx already points to it
    search_str = f'("{war_id}",'
    idx = content.find(search_str)
    if idx == -1:
        print(f"WARNING: _replace_war_entry could not find entry for {war_id}")
        return content

    entry_start = idx  # idx IS the '(' — no need to step back

    # Find the first """ — opening of the data block
    open_tq = content.find('"""', entry_start)
    if open_tq == -1:
        return content

    # Find the second """ — closing of the data block
    close_tq = content.find('"""', open_tq + 3)
    if close_tq == -1:
        return content

    # Find the ')' that ends the tuple after the closing """
    close_paren = content.find(')', close_tq + 3)
    if close_paren == -1:
        return content

    entry_end = close_paren + 1  # exclusive
    return content[:entry_start] + new_entry + content[entry_end:]


def update_build_tracker(war_data, war_id_extra="", is_cwl=False):
    state = war_data.get("state", "")

    if state == "notInWar":
        return False

    with open(TRACKER_PY, "r") as f:
        content = f.read()

    war_id, new_entry, in_prog = build_war_block(war_data, war_id_extra, is_cwl=is_cwl)

    id_pattern = re.compile(rf'"\s*{re.escape(war_id)}\s*"')
    war_exists  = bool(id_pattern.search(content))

    blocks_start = re.search(r'WAR_BLOCKS\s*=\s*\[', content)
    if not blocks_start:
        print("ERROR: Could not find WAR_BLOCKS in build_tracker.py")
        return False

    insert_pos = blocks_start.end()

    if not war_exists:
        print(f"New war detected (ID {war_id}). Adding to tracker.")
        content = content[:insert_pos] + "\n" + new_entry + ",\n" + content[insert_pos:]
    else:
        print(f"War {war_id} exists. Updating entry.")
        # Use safe string-based replacement — the regex approach with .*? + DOTALL
        # can match across multiple entries when run over the full file.
        content = _replace_war_entry(content, war_id, new_entry)

    if state == "warEnded":
        result = determine_result(war_data)
        result_pat = re.compile(r'RESULTS\s*=\s*\{')
        results_start = result_pat.search(content)
        if results_start:
            # Check only within the RESULTS section (not the whole file —
            # the war_id also appears in WAR_BLOCKS and would always match).
            results_section = content[results_start.end():results_start.end() + 8000]
            if war_id not in results_section:
                insert_at = results_start.end()
                content = content[:insert_at] + f'\n    "{war_id}": "{result}",' + content[insert_at:]
                print(f"War {war_id} ended. Result: {result}")
            else:
                print(f"War {war_id} result already in RESULTS, skipping.")

    content, _ = update_player_tags(war_data, content)

    with open(TRACKER_PY, "w") as f:
        f.write(content)

    return True


def fetch_cwl_wars():
    """Fetch all CWL wars for the current league season where our clan participated."""
    try:
        group = api_get(f"/clans/{CLAN_TAG}/currentwar/leaguegroup")
    except Exception as e:
        print(f"CWL: no active league group ({e})")
        return []

    state = group.get("state", "")
    print(f"CWL group state: {state}")
    if state == "notInWar":
        return []

    wars = []
    for round_num, round_data in enumerate(group.get("rounds", []), 1):
        for war_tag in round_data.get("warTags", []):
            if war_tag == "#0":
                continue  # round not yet scheduled
            encoded = war_tag.replace("#", "%23")
            try:
                war = api_get(f"/clanwarleagues/wars/{encoded}")
            except Exception as e:
                print(f"CWL round {round_num} war {war_tag}: fetch error ({e})")
                continue

            clan_tag  = war.get("clan",     {}).get("tag", "")
            opp_tag   = war.get("opponent", {}).get("tag", "")

            if clan_tag != OUR_TAG and opp_tag != OUR_TAG:
                continue  # we're not in this war

            if opp_tag == OUR_TAG:
                # Flip so our clan is always in "clan" field
                war["clan"], war["opponent"] = war["opponent"], war["clan"]

            wars.append((round_num, war))
            print(f"CWL round {round_num}: found our war vs {war['opponent']['name']} (state={war.get('state','')})")

    return wars


def update_war_end_iso(iso_str):
    """Write war endTime ISO string (or '') to WAR_END_ISO in build_tracker.py.
    JS uses this to show smart-capture time as 'Next update' instead of next cron slot.
    """
    with open(TRACKER_PY, "r") as f:
        content = f.read()
    content = re.sub(
        r'^WAR_END_ISO\s*=\s*"[^"]*"',
        f'WAR_END_ISO = "{iso_str}"',
        content, flags=re.MULTILINE
    )
    with open(TRACKER_PY, "w") as f:
        f.write(content)


def wait_for_war_end(war_data):
    """
    If a war is active (inWar) and its endTime is within the next 4 hours,
    sleep until end + 3-min buffer and return True so caller can re-fetch final data.
    Wars ending > 4 h away fall through to the next regular 4-h cron cycle.
    """
    if war_data.get("state") != "inWar":
        return False

    end_time_str = war_data.get("endTime", "")
    if not end_time_str:
        print("inWar but API returned no endTime — skipping smart wait")
        return False

    end_dt  = datetime.strptime(end_time_str[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    secs_remaining = (end_dt - now_utc).total_seconds()

    BUFFER   = 180          # 3 min after war ends before re-fetching
    MAX_WAIT = 4 * 3600     # only wait if war ends within 4 h

    if secs_remaining < 0:
        print(f"War already ended {-secs_remaining / 60:.0f} min ago — no wait needed")
        return False

    if secs_remaining > MAX_WAIT:
        print(f"War ends in {secs_remaining / 3600:.1f} h — next cron cycle will capture final data")
        return False

    wait_secs = secs_remaining + BUFFER
    end_str   = end_dt.strftime("%Y-%m-%d %H:%M UTC")
    print(f"War ends at {end_str} ({secs_remaining / 60:.0f} min away). "
          f"Sleeping {wait_secs / 60:.0f} min for precise end-of-war capture…")
    time.sleep(wait_secs)
    print("War end window reached. Fetching final data…")
    return True


def main():
    if not API_KEY:
        print("ERROR: COC_API_KEY not set")
        sys.exit(1)

    any_changed = False

    # ── 0. Sync clan roster (members joined / left, TH upgrades) ─────────────
    print("Syncing clan roster...")
    try:
        with open(TRACKER_PY, "r") as f:
            _rc = f.read()
        _rc, _roster_changed = update_roster(_rc)
        if _roster_changed:
            with open(TRACKER_PY, "w") as f:
                f.write(_rc)
            any_changed = True
            print("Roster updated.")
        else:
            print("Roster unchanged.")
    except Exception as e:
        print(f"Roster sync error: {e}")

    # ── 1. Regular war ────────────────────────────────────────────────────────
    print("Fetching current war...")
    try:
        war_data = api_get(f"/clans/{CLAN_TAG}/currentwar")
        state    = war_data.get("state", "unknown")
        print(f"Regular war state: {state}")
        changed = update_build_tracker(war_data)
        any_changed = any_changed or changed

        # Update WAR_END_ISO so the tracker can show accurate "Next update" time.
        # inWar → store endTime ISO; anything else → clear it.
        if state == "inWar":
            end_str = war_data.get("endTime", "")
            if end_str:
                end_dt = datetime.strptime(end_str[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
                update_war_end_iso(end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
                any_changed = True   # need to regen HTML with updated end time
        else:
            update_war_end_iso("")   # clear when no active war

        # Smart end-of-war capture: if inWar and ending within 4 h,
        # sleep until the war ends then re-fetch final results.
        if wait_for_war_end(war_data):
            war_data_final = api_get(f"/clans/{CLAN_TAG}/currentwar")
            print(f"Post-end war state: {war_data_final.get('state', 'unknown')}")
            changed = update_build_tracker(war_data_final)
            any_changed = any_changed or changed
            update_war_end_iso("")   # war ended — clear the end time

    except Exception as e:
        print(f"Regular war API error: {e}")

    # ── 2. CWL wars ───────────────────────────────────────────────────────────
    print("Fetching CWL wars...")
    cwl_wars = fetch_cwl_wars()
    for round_num, war in cwl_wars:
        # Use opponent tag as extra to keep IDs unique if rounds share a start time
        extra = war.get("opponent", {}).get("tag", f"r{round_num}")
        changed = update_build_tracker(war, war_id_extra=extra, is_cwl=True)
        any_changed = any_changed or changed

    # ── 3. Regenerate HTML if anything changed ────────────────────────────────
    if any_changed:
        print("Regenerating HTML...")
        result = subprocess.run(
            ["python3", TRACKER_PY],
            capture_output=True, text=True, cwd=SCRIPT_DIR
        )
        if result.returncode == 0:
            print("HTML regenerated successfully.")
        else:
            print(f"ERROR regenerating HTML:\n{result.stderr}")
            sys.exit(1)
    else:
        print("No changes made.")


if __name__ == "__main__":
    main()
