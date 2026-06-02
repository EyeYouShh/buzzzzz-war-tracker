#!/usr/bin/env python3
"""
Buzzzzz War Tracker — Automation Script
Fetches current war from CoC API and updates build_tracker.py, then regenerates HTML.
"""

import os, sys, re, json, subprocess
from datetime import datetime, timezone
import urllib.request

API_KEY = os.environ.get("COC_API_KEY", "")
CLAN_TAG = "%232GGL80JL0"
BASE_URL = "https://api.clashofclans.com/v1"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKER_PY = os.path.join(SCRIPT_DIR, "build_tracker.py")
TRACKER_HTML = os.path.join(SCRIPT_DIR, "buzzzzz-war-tracker.html")


def api_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def war_id_from_start(start_time_str):
    """Convert API startTime '20260529T120000.000Z' to a numeric ID string."""
    # Strip non-digits to get YYYYMMDDHHmmss → use last 9 digits like ClashSpot IDs
    digits = re.sub(r"\D", "", start_time_str)[:14]
    return str(int(digits) % 10_000_000_000)


def format_war_date(start_time_str):
    """'20260529T120000.000Z' → '5/29/26'"""
    dt = datetime.strptime(start_time_str[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    return dt.strftime("%-m/%-d/%y")


def build_war_block(war_data):
    """Convert API war data to v2 WAR_BLOCK format lines.
    V2 row: #tag|name|pos|TH|atk_count|raw_stars|net_stars|defPos:rawStars:delta:defTH,...
    """
    our_clan = war_data["clan"]
    opponent = war_data["opponent"]

    # Lookup tables for opponent members (keyed by tag)
    def_pos = {m["tag"]: m["mapPosition"]          for m in opponent.get("members", [])}
    def_th  = {m["tag"]: m.get("townHallLevel", 0) for m in opponent.get("members", [])}

    size     = war_data.get("teamSize", "?")
    war_id   = war_id_from_start(war_data["startTime"])
    date     = format_war_date(war_data["startTime"])
    opp_name = opponent["name"].replace('"', '\\"').replace('\n', ' ').replace('\r', '')
    war_size = f"{size}v{size}"
    state    = war_data.get("state", "")
    in_prog  = state in ("preparation", "inWar")

    # ── Pass 1: collect all attacks per defender base for delta computation ──
    attacks_on_base = {}   # defenderTag → [{order, stars, attackerTag}]
    for m in our_clan.get("members", []):
        for a in m.get("attacks", []):
            dt = a["defenderTag"]
            attacks_on_base.setdefault(dt, []).append({
                "order": a.get("order", 0),
                "stars": a["stars"],
                "attackerTag": a["attackerTag"],
            })

    # ── Compute per-attack delta (new stars contributed to war total) ──
    delta_map = {}   # (defenderTag, order) → delta
    for def_tag, atk_list in attacks_on_base.items():
        running_max = 0
        for atk in sorted(atk_list, key=lambda x: x["order"]):
            delta = max(0, atk["stars"] - running_max)
            delta_map[(def_tag, atk["order"])] = delta
            running_max = max(running_max, atk["stars"])

    # ── Pass 2: build per-member v2 rows ──
    rows = []
    for m in sorted(our_clan.get("members", []), key=lambda x: x["mapPosition"]):
        tag  = m["tag"]
        name = m["name"].replace('"""', '"').replace('\n', ' ').replace('\r', '').replace('|', '-')
        pos  = m["mapPosition"]
        th   = m.get("townHallLevel", 0)
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

    if in_prog:
        entry = f'("{war_id}","{date}","{opp_name}","{war_size}","""\n{block_lines}\n""", True)'
    else:
        entry = f'("{war_id}","{date}","{opp_name}","{war_size}","""\n{block_lines}\n""")'

    return war_id, entry, in_prog


def update_player_tags(war_data, content):
    """Keep PLAYER_TAGS dict in build_tracker.py current with our clan members' tag→name mapping."""
    members = war_data.get("clan", {}).get("members", [])
    if not members:
        return content, False

    tags_match = re.search(r'PLAYER_TAGS\s*=\s*\{([^}]*)\}', content, re.DOTALL)
    if not tags_match:
        print("WARNING: PLAYER_TAGS block not found in build_tracker.py")
        return content, False

    # Parse existing entries
    existing = {}
    for m in re.finditer(r'"(#[^"]+)"\s*:\s*"([^"]*)"', tags_match.group(1)):
        existing[m.group(1)] = m.group(2)

    # Update from current war roster
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


def determine_result(war_data):
    """Return 'W', 'L', or 'D' based on final war state."""
    our = war_data["clan"]
    opp = war_data["opponent"]
    our_stars = our.get("stars", 0)
    opp_stars = opp.get("stars", 0)
    our_dest = our.get("destructionPercentage", 0)
    opp_dest = opp.get("destructionPercentage", 0)
    if our_stars > opp_stars:
        return "W"
    elif our_stars < opp_stars:
        return "L"
    elif our_dest > opp_dest:
        return "W"
    elif our_dest < opp_dest:
        return "L"
    return "D"


def update_build_tracker(war_data):
    state = war_data.get("state", "")

    if state == "notInWar":
        print("No active war. Nothing to update.")
        return False

    with open(TRACKER_PY, "r") as f:
        content = f.read()

    war_id, new_entry, in_prog = build_war_block(war_data)

    id_pattern = re.compile(rf'"\s*{re.escape(war_id)}\s*"')
    war_exists = bool(id_pattern.search(content))

    # Find WAR_BLOCKS insertion point (after the opening bracket)
    blocks_start = re.search(r'WAR_BLOCKS\s*=\s*\[', content)
    if not blocks_start:
        print("ERROR: Could not find WAR_BLOCKS in build_tracker.py")
        return False

    insert_pos = blocks_start.end()

    if not war_exists:
        print(f"New war detected (ID {war_id}). Adding to tracker.")
        # Insert at top of WAR_BLOCKS
        content = content[:insert_pos] + "\n" + new_entry + ",\n" + content[insert_pos:]
    else:
        print(f"War {war_id} exists. Updating entry.")
        # Replace the old entry (handles both in-progress and completed)
        # Match from the war_id to the closing ), possibly with True/False flags
        old_entry_pat = re.compile(
            r'\("?\s*' + re.escape(war_id) + r'\s*"?,.*?"""\)',
            re.DOTALL
        )
        content = old_entry_pat.sub(new_entry, content)

    # If war ended, add/update RESULTS
    if state == "warEnded":
        result = determine_result(war_data)
        result_pat = re.compile(r'RESULTS\s*=\s*\{')
        results_start = result_pat.search(content)
        if results_start:
            # Check if war_id already in RESULTS
            if f'"{war_id}"' not in content:
                insert_at = results_start.end()
                content = content[:insert_at] + f'\n    "{war_id}": "{result}",' + content[insert_at:]
                print(f"War {war_id} ended. Result: {result}")

    # Always keep PLAYER_TAGS current with latest tag→name mapping
    content, tags_changed = update_player_tags(war_data, content)

    with open(TRACKER_PY, "w") as f:
        f.write(content)

    return True


def main():
    if not API_KEY:
        print("ERROR: COC_API_KEY not set")
        sys.exit(1)

    print("Fetching current war...")
    try:
        war_data = api_get(f"/clans/{CLAN_TAG}/currentwar")
    except Exception as e:
        print(f"API error: {e}")
        sys.exit(1)

    state = war_data.get("state", "unknown")
    print(f"War state: {state}")

    changed = update_build_tracker(war_data)

    if changed:
        print("Regenerating HTML...")
        result = subprocess.run(
            ["python3", TRACKER_PY],
            capture_output=True, text=True, cwd=SCRIPT_DIR
        )
        if result.returncode == 0:
            print("HTML regenerated successfully.")
        else:
            print(f"ERROR regenerating HTML: {result.stderr}")
            sys.exit(1)
    else:
        print("No changes made.")


if __name__ == "__main__":
    main()
