#!/usr/bin/env python3
"""
Backfill W/L/D results for all historical CWL rounds by querying the CoC API.

Alphanumeric CWL war IDs (e.g. 8Q0J0022Q) ARE the CoC API warTags — fetch
/clanwarleagues/wars/{id} for each, compute stars vs stars (then dest% on tie),
and write the result into RESULTS in build_tracker.py.

Numeric IDs (e.g. 317373071) are current-season rounds tracked by the
regular runner — those get results automatically after the fix to the
RESULTS check in update_tracker.py.

Run via: python3 scripts/backfill_cwl_results.py
Requires: COC_API_KEY env var
"""

import os, re, sys, time, json, subprocess
from urllib.request import urlopen, Request
from urllib.error import HTTPError

API_KEY  = os.environ.get("COC_API_KEY", "")
BASE_URL = "https://api.clashofclans.com/v1"

# Resolve path relative to this script so it works wherever it's called from
SCRIPTS_DIR  = os.path.dirname(os.path.abspath(__file__))
TRACKER_PY   = os.path.join(SCRIPTS_DIR, "..", "build_tracker.py")

if not API_KEY:
    print("ERROR: COC_API_KEY not set"); sys.exit(1)


def api_get(path):
    req = Request(f"{BASE_URL}{path}", headers={"Authorization": f"Bearer {API_KEY}"})
    resp = urlopen(req, timeout=15)
    return json.loads(resp.read())


def determine_result(war_data):
    """Stars wins. Tie → destruction %. Both tied → Draw."""
    our = war_data["clan"]
    opp = war_data["opponent"]
    our_st = our.get("stars", 0);     opp_st = opp.get("stars", 0)
    our_d  = our.get("destructionPercentage", 0)
    opp_d  = opp.get("destructionPercentage", 0)
    if   our_st > opp_st: return "W"
    elif our_st < opp_st: return "L"
    elif our_d  > opp_d:  return "W"
    elif our_d  < opp_d:  return "L"
    return "D"


def update_results(content, war_id, result, existing_result=None):
    """
    Insert or update the RESULTS entry for war_id.
    Handles both single-quoted and double-quoted existing keys.
    """
    # Check if already in RESULTS section (search ~10KB from RESULTS = {)
    results_pat = re.compile(r'RESULTS\s*=\s*\{')
    rs = results_pat.search(content)
    if not rs:
        print("  ERROR: RESULTS dict not found"); return content

    results_window = content[rs.end():rs.end() + 10000]

    if war_id in results_window:
        # Update existing entry — match either quote style
        content = re.sub(
            rf"""(['"]{re.escape(war_id)}['"])\s*:\s*['"]([WLD])['"]""",
            lambda m: m.group(1) + f": '{result}'",
            content,
            count=1
        )
    else:
        # Insert new entry at the top of RESULTS
        insert_at = rs.end()
        content = content[:insert_at] + f"\n    '{war_id}': '{result}'," + content[insert_at:]

    return content


# ── Main ─────────────────────────────────────────────────────────────────────

with open(TRACKER_PY) as f:
    content = f.read()

# Extract all alphanumeric CWL war IDs from WAR_BLOCKS
# These match CoC's warTag pattern (8 or 9 uppercase alphanumeric chars starting with a digit)
# Exclude pure-numeric IDs (those are current-season, handled by the runner)
cwl_id_pat = re.compile(r'\("([0-9][A-Z0-9]{7,8})",')
cwl_ids = list(dict.fromkeys(cwl_id_pat.findall(content)))  # deduplicated, preserving order

print(f"Found {len(cwl_ids)} historical CWL war IDs to backfill\n")

updated = []
unchanged = []
not_ended = []
failed = []

for war_id in cwl_ids:
    try:
        war_data = api_get(f"/clanwarleagues/wars/{war_id}")
        state = war_data.get("state", "unknown")

        if state != "warEnded":
            print(f"  {war_id}  state={state}  — skipping (not ended)")
            not_ended.append(war_id)
            time.sleep(0.05)
            continue

        result = determine_result(war_data)
        our_st = war_data["clan"].get("stars", "?")
        opp_st = war_data["opponent"].get("stars", "?")
        opp    = war_data["opponent"].get("name", "?")

        # Check what's currently set (if anything)
        rs_match = re.search(r'RESULTS\s*=\s*\{', content)
        existing = None
        if rs_match:
            win = content[rs_match.end():rs_match.end()+10000]
            m = re.search(rf"""['"]{re.escape(war_id)}['"]\s*:\s*['"]([WLD])['"]""", win)
            if m:
                existing = m.group(1)

        if existing == result:
            print(f"  {war_id}  {our_st}★ vs {opp_st}★  vs {opp[:20]:<20}  → {result}  (unchanged)")
            unchanged.append(war_id)
        else:
            prev = f" (was {existing})" if existing else " (new)"
            print(f"  {war_id}  {our_st}★ vs {opp_st}★  vs {opp[:20]:<20}  → {result}{prev}")
            content = update_results(content, war_id, result, existing)
            updated.append(war_id)

        time.sleep(0.1)  # respect rate limit

    except HTTPError as e:
        print(f"  {war_id}  HTTP {e.code} — API unavailable (too old or invalid)")
        failed.append(war_id)
        time.sleep(0.1)
    except Exception as e:
        print(f"  {war_id}  ERROR: {e}")
        failed.append(war_id)

# Write back
with open(TRACKER_PY, "w") as f:
    f.write(content)

print(f"""
Results:
  Updated : {len(updated)}  {updated}
  Unchanged: {len(unchanged)}
  Not ended: {len(not_ended)}  {not_ended}
  API fail : {len(failed)}  {failed}
""")

# Rebuild HTML
print("Rebuilding HTML...")
r = subprocess.run(["python3", TRACKER_PY], capture_output=True, text=True,
                   cwd=os.path.dirname(TRACKER_PY))
if r.returncode == 0:
    print("HTML rebuilt OK")
else:
    print(f"ERROR rebuilding HTML:\n{r.stderr}")
    sys.exit(1)
