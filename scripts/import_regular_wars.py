#!/usr/bin/env python3
"""
Import v2 regular war data from scraped_wars_v2.json into build_tracker.py.

Actions:
  1. Fill missing dates from scraped_wars.json fallback
  2. Replace v1 blocks for 22 existing regular wars with v2 data
  3. Insert 35 new regular wars (Nov'25 – Mar'26) in chronological order
  4. Update RESULTS dict for new wars (default 'W' — needs manual review)
"""
import json, re, sys

# ── Load data ──────────────────────────────────────────────────────────────────
with open('scraped_wars_v2.json') as f:
    v2_raw = json.load(f)
with open('scraped_wars.json') as f:
    v1_meta = json.load(f)
with open('build_tracker.py') as f:
    content = f.read()

# ── Build date fallback map ────────────────────────────────────────────────────
v1_dates = {w['warId']: w['endDate'] for w in v1_meta}
v1_results = {}  # We'll infer W/L/D from existing RESULTS in build_tracker.py

# ── Filter good entries (skip warId=? and empty blocks) ───────────────────────
wars = []
for w in v2_raw:
    wid = w.get('warId', '?')
    if wid == '?' or not w.get('block') or w.get('size', 0) == 0:
        continue
    # Fill missing dates from v1 metadata
    if not w.get('endDate') and wid in v1_dates:
        w['endDate'] = v1_dates[wid]
    # Fix block date too if it was empty
    if w['endDate']:
        w['block'] = w['block'].replace('("'+wid+'","",', '("'+wid+'","'+w['endDate']+'",')
    wars.append(w)

wars_by_id = {w['warId']: w for w in wars}
print(f'Loaded {len(wars)} good v2 war entries')

# ── Protected IDs (perfect API v2 — never touch) ──────────────────────────────
PROTECTED = {'417523054', '317373071', '217372345'}

# ── Find all existing WAR_BLOCK IDs in tracker ────────────────────────────────
existing_ids = set(re.findall(r'\("(\w+)",', content))
# Filter to only WAR_BLOCKS section (before RESULTS)
wb_end = content.find('# ── Win/Loss')
wb_section = content[:wb_end]
tracker_war_ids = set(re.findall(r'\("(\w+)",', wb_section))

print(f'Existing WAR_BLOCK IDs in tracker: {len(tracker_war_ids)}')

def find_entry_bounds(text, war_id):
    """Find (start, end) char positions of a WAR_BLOCKS tuple."""
    search = f'("{war_id}",'
    idx = text.find(search)
    if idx == -1:
        return None, None
    line_start = text.rfind('\n', 0, idx)
    line_start = 0 if line_start == -1 else line_start + 1
    tq_start = text.find('"""', idx)
    if tq_start == -1:
        return None, None
    tq_end = text.find('"""', tq_start + 3)
    if tq_end == -1:
        return None, None
    after_tq = text[tq_end + 3:]
    # Match optional flags: , False, False) or , False, True) or just )
    close_match = re.match(r',\s*(True|False),\s*(True|False)\)', after_tq)
    if close_match:
        end_idx = tq_end + 3 + close_match.end()
    else:
        close_match2 = re.match(r'\)', after_tq)
        if close_match2:
            end_idx = tq_end + 3 + close_match2.end()
        else:
            return None, None
    if end_idx < len(text) and text[end_idx] == ',':
        end_idx += 1
    if end_idx < len(text) and text[end_idx] == '\n':
        end_idx += 1
    return line_start, end_idx

# ── Step 1: Replace existing v1 regular wars with v2 ─────────────────────────
print('\n=== Step 1: Upgrade existing regular wars v1 → v2 ===')
upgraded = 0
for wid, w in wars_by_id.items():
    if wid in PROTECTED:
        continue
    if wid not in tracker_war_ids:
        continue
    block = w['block'].strip()
    if not block:
        print(f'  ✗ {wid} has empty block')
        continue
    start, end = find_entry_bounds(content, wid)
    if start is None:
        print(f'  ✗ Could not find {wid} in tracker')
        continue
    content = content[:start] + '\n' + block + '\n' + content[end:]
    upgraded += 1
    print(f'  ✓ {wid} ({w.get("opponent","?")} {w.get("endDate","")}) v1→v2 sz={w.get("size",0)}')

print(f'  Upgraded {upgraded} entries')

# ── Step 2: Insert new regular wars ──────────────────────────────────────────
print('\n=== Step 2: Insert new regular wars ===')

# Find wars not yet in tracker
new_wars = [w for w in wars if w['warId'] not in tracker_war_ids and w['warId'] not in PROTECTED]

def parse_date_key(w):
    d = w.get('endDate', '1/1/00')
    try:
        parts = d.split('/')
        m, day, yr = int(parts[0]), int(parts[1]), int(parts[2])
        yr_full = yr + 2000
        return (yr_full, m, day)
    except:
        return (0, 0, 0)

new_wars.sort(key=parse_date_key, reverse=True)  # newest first
print(f'  {len(new_wars)} new wars to insert')

# Find the WAR_BLOCKS closing bracket (] before RESULTS)
wb_close = content.find('\n]\n\n# ── Win/Loss')
if wb_close == -1:
    wb_close = content.find('\n]\n\n#')
if wb_close == -1:
    print('  ✗ Cannot find WAR_BLOCKS closing bracket!')
    sys.exit(1)

insert_text = ''
for w in new_wars:
    block = w['block'].strip()
    if block:
        insert_text += '\n' + block + '\n'
        print(f'  + {w["warId"]} | {w.get("endDate","?")} | {w.get("opponent","?")} | sz={w.get("size",0)}')

content = content[:wb_close] + insert_text + content[wb_close:]
print(f'  Inserted {len(new_wars)} new wars')

# ── Step 3: Update RESULTS dict ───────────────────────────────────────────────
print('\n=== Step 3: Update RESULTS dict ===')

results_match = re.search(r'(RESULTS\s*=\s*\{)(.*?)(\})', content, re.DOTALL)
if not results_match:
    print('  ✗ Cannot find RESULTS dict!')
    sys.exit(1)

results_text = results_match.group(2)
existing_results_ids = set(re.findall(r"'(\w+)':", results_text))

# Add new wars to RESULTS
new_results_lines = '\n    # Regular wars (historical, pre-automation) — verify W/L/D\n'
added = 0
for w in new_wars:
    wid = w['warId']
    if wid not in existing_results_ids:
        opp = w.get('opponent', '?')
        date = w.get('endDate', '?')
        new_results_lines += f"    '{wid}': 'W',  # {opp} ({date})\n"
        added += 1

results_close = results_match.start(3)
content = content[:results_close] + new_results_lines + content[results_close:]
print(f'  Added {added} entries to RESULTS (default W — verify each)')

# ── Step 4: Validate and write ────────────────────────────────────────────────
print('\n=== Step 4: Writing build_tracker.py ===')
new_entry_count = len(re.findall(r'\("\w+","[^"]+","[^"]+","[^"]+","""', content))
print(f'  WAR_BLOCKS entries: {new_entry_count} (was 67)')

# Quick syntax check
try:
    compile(content, 'build_tracker.py', 'exec')
    print('  ✓ Syntax OK')
except SyntaxError as e:
    print(f'  ✗ Syntax error: {e}')
    sys.exit(1)

with open('build_tracker.py', 'w') as f:
    f.write(content)

print(f'\n✅ Done!')
print(f'  Upgraded to v2: {upgraded}')
print(f'  New wars inserted: {len(new_wars)}')
print(f'  RESULTS entries added: {added}')
print(f'  Total WAR_BLOCKS: {new_entry_count}')
print('\n⚠️  RESULTS for new historical wars default to W — please verify.')
