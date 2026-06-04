#!/usr/bin/env python3
"""
Import historical war data from scraped_wars.json + scraped_cwl.json into build_tracker.py.

Actions:
  1. Upgrade 273131437 (Friendj of wer) v1 → v2 (has scraped block)
  2. Replace v1 blocks for 14 existing CWL entries with v2 data
  3. Insert 28 new CWL entries (Mar/Feb/Jan/Dec 2025) at end of WAR_BLOCKS
  4. Fix December 2025 CWL dates: "2/X/25" → "12/X/25"
  5. Update RESULTS dict with new CWL entries
"""
import json, re, sys

# ── Load data ──────────────────────────────────────────────────────────────────
with open('scraped_wars.json') as f:
    wars_data = json.load(f)
with open('scraped_cwl.json') as f:
    cwl_data = json.load(f)
with open('build_tracker.py') as f:
    content = f.read()

# ── Constants ──────────────────────────────────────────────────────────────────
PROTECTED = {'417523054', '317373071', '217372345'}  # perfect API v2 — never touch

# December 2025 CWL round IDs (date was extracted wrong as "2/X/25" → "12/X/25")
DEC_CWL_IDS = {'8QJJURPPC','8QJVLPVV2','8QC2VJ8CR','8QCPQ2JVY','8QCQ0VUQ2','8QCRGJC22','8QCCR22LC'}

# CWL IDs currently in tracker with v1 data (need upgrading)
TRACKER_CWL_IDS = {
    '8Q0J0022Q','8Q0G02CGY','8Q0L0VR82','8Q0P0CYLR','8Q0882R82','8Q0020RCC','8LVUPY0R9',
    '8LGRLVYU9','8LGQYCQQ2','8LGY9RLGQ','8LG98L2PC','8LG0VRGUQ','8LQUVPLJ9','8LQCG02G9',
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def fix_dec_date(s):
    """Fix December 2025 CWL dates: '2/X/25' → '12/X/25' in the block string."""
    return re.sub(r'"2/(\d+)/25"', r'"12/\1/25"', s)

def get_block(entry):
    """Return the full block string from a scraped JSON entry, with date fix if needed."""
    block = entry.get('block', '')
    if not block:
        return None
    if entry['warId'] in DEC_CWL_IDS:
        block = fix_dec_date(block)
    # Ensure block ends with consistent formatting
    if not block.endswith('\n'):
        block = block.rstrip()
    return block

def find_entry_bounds(text, war_id):
    """
    Find start and end character positions of a WAR_BLOCKS tuple for given war_id.
    Returns (start, end) inclusive of leading newline and trailing comma+newline,
    or (None, None) if not found.
    """
    # Pattern: ("warId", ... through closing ), with optional flags
    # We look for the tuple start, then scan forward to find the matching close
    search = f'("{war_id}",'
    idx = text.find(search)
    if idx == -1:
        return None, None

    # Walk backward to include any leading blank line/newline before the tuple
    line_start = text.rfind('\n', 0, idx)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1  # skip the newline itself — we'll keep the blank line above

    # Now find the end: we need to find """), or """, X, Y), accounting for triple-quote content
    # Find the triple-quote block start
    tq_start = text.find('"""', idx)
    if tq_start == -1:
        return None, None
    # Find matching closing triple-quote (after tq_start + 3)
    tq_end = text.find('"""', tq_start + 3)
    if tq_end == -1:
        return None, None
    # After the closing """, find the end of the tuple: ), or , X, Y),
    after_tq = text[tq_end + 3:]
    close_match = re.match(r',\s*(True|False),\s*(True|False)\)|', after_tq)
    if close_match:
        end_idx = tq_end + 3 + close_match.end()
    else:
        # Try simple ),
        close_match2 = re.match(r'\)', after_tq)
        if close_match2:
            end_idx = tq_end + 3 + close_match2.end()
        else:
            return None, None
    # Include the trailing comma
    if end_idx < len(text) and text[end_idx] == ',':
        end_idx += 1
    # Include trailing newline
    if end_idx < len(text) and text[end_idx] == '\n':
        end_idx += 1

    return line_start, end_idx

def entry_to_str(block_str):
    """Ensure a block string from scraped JSON is properly formatted for insertion."""
    # The block strings from scraped_cwl.json are already full tuple strings like:
    # ("warId","date","opp","size","""\n...\n""", False, True),
    # We just need to ensure there's a trailing newline
    s = block_str.strip()
    if not s.endswith(','):
        s += ','
    return '\n' + s + '\n'

# ── Build lookup for scraped CWL data ──────────────────────────────────────────
cwl_by_id = {c['warId']: c for c in cwl_data}

# ── Step 1: Upgrade regular war 273131437 (Friendj of wer) v1 → v2 ────────────
# Skipped: the scraped block for 273131437 is truncated (only 15/30 players + "...")
# The original v1 block in build_tracker.py is more complete. Leave it as-is.
print("=== Step 1: Upgrade 273131437 (Friendj of wer) v1 → v2 ===")
print("  ⚠ Skipped — scraped block is truncated (ends with '...'). Keeping original v1 data.")

# ── Step 2: Replace v1 → v2 for 14 existing CWL entries ──────────────────────
print("\n=== Step 2: Upgrade existing CWL v1 → v2 ===")
upgraded = 0
for wid in TRACKER_CWL_IDS:
    if wid not in cwl_by_id:
        print(f"  ✗ {wid} not in scraped CWL data")
        continue
    entry = cwl_by_id[wid]
    block = get_block(entry)
    if not block:
        print(f"  ✗ {wid} has no block data")
        continue

    start, end = find_entry_bounds(content, wid)
    if start is None:
        print(f"  ✗ Could not find {wid} in file")
        continue

    new_entry = '\n' + block.strip() + '\n'
    content = content[:start] + new_entry + content[end:]
    upgraded += 1
    print(f"  ✓ Replaced {wid} ({entry.get('opponent','?')}) v1→v2")

print(f"  Upgraded {upgraded}/{len(TRACKER_CWL_IDS)} CWL entries")

# ── Step 3: Insert 28 new CWL entries (newest first within each month) ─────────
print("\n=== Step 3: Insert new CWL entries ===")

# Determine which CWL IDs are new (not yet in tracker)
existing_tracker_ids = set(re.findall(r'\("(\w+)",', content))
new_cwl_entries = [c for c in cwl_data
                   if c['warId'] not in existing_tracker_ids
                   and c['warId'] not in PROTECTED]

print(f"  Found {len(new_cwl_entries)} new CWL entries to insert")

# Sort by date descending (newest first) — parse M/D/YY dates
def parse_date_key(entry):
    d = entry.get('endDate', '1/1/00')
    # Fix Dec dates before sorting
    if entry['warId'] in DEC_CWL_IDS:
        d = re.sub(r'^2/', '12/', d)
    try:
        m, day, yr = d.split('/')
        yr_full = int(yr) + 2000
        return (yr_full, int(m), int(day))
    except:
        return (0, 0, 0)

new_cwl_entries.sort(key=parse_date_key, reverse=True)

# Build the insertion text
insert_text = ''
inserted = 0
for entry in new_cwl_entries:
    block = get_block(entry)
    if not block:
        print(f"  ✗ {entry['warId']} has no block data")
        continue
    insert_text += '\n' + block.strip() + '\n'
    inserted += 1
    date = entry.get('endDate','?')
    if entry['warId'] in DEC_CWL_IDS:
        date = re.sub(r'^2/', '12/', date)
    print(f"  + {entry['warId']} | {date} | {entry.get('opponent','?')}")

# Find the closing ] of WAR_BLOCKS and insert before it
# The WAR_BLOCKS ends with the last entry followed by ']'
wb_close = content.find('\n]\n\n# ── Win/Loss')
if wb_close == -1:
    wb_close = content.find('\n]\n\n#')
if wb_close == -1:
    # Try alternate pattern
    wb_close = content.rfind('"""),\n\n]')
    if wb_close != -1:
        wb_close += len('"""),\n')

if wb_close == -1:
    print("  ✗ Could not find WAR_BLOCKS closing bracket!")
    sys.exit(1)

content = content[:wb_close] + insert_text + content[wb_close:]
print(f"\n  Inserted {inserted} new CWL entries")

# ── Step 4: Update RESULTS dict ───────────────────────────────────────────────
print("\n=== Step 4: Update RESULTS dict ===")

# Find the RESULTS dict and its closing brace
results_match = re.search(r'(RESULTS\s*=\s*\{)(.*?)(\})', content, re.DOTALL)
if not results_match:
    print("  ✗ Could not find RESULTS dict!")
    sys.exit(1)

results_text = results_match.group(2)
existing_results_ids = set(re.findall(r"'(\w+)':", results_text))

# Build new RESULTS entries for CWL seasons
# Group by season
seasons = {
    'Mar 2026': [],
    'Feb 2026': [],
    'Jan 2026': [],
    'Dec 2025': [],
}
season_map = {}
for entry in new_cwl_entries:
    wid = entry['warId']
    date = entry.get('endDate', '1/1/00')
    if wid in DEC_CWL_IDS:
        season_map[wid] = 'Dec 2025'
        seasons['Dec 2025'].append(wid)
    elif date.endswith('/26'):
        m = int(date.split('/')[0])
        if m == 3:
            season_map[wid] = 'Mar 2026'
            seasons['Mar 2026'].append(wid)
        elif m == 2:
            season_map[wid] = 'Feb 2026'
            seasons['Feb 2026'].append(wid)
        elif m == 1:
            season_map[wid] = 'Jan 2026'
            seasons['Jan 2026'].append(wid)

# Build insertion lines for RESULTS
new_results_lines = '\n    # CWL historical seasons (defaulting to W — verify individual rounds)\n'
for season_name, ids in seasons.items():
    if not ids:
        continue
    pairs = ', '.join(f"'{wid}': 'W'" for wid in ids)
    new_results_lines += f'    # CWL {season_name} — Buzzzzz\n'
    new_results_lines += f'    {pairs},\n'

# Insert before the closing } of RESULTS
results_close = results_match.start(3)
content = content[:results_close] + new_results_lines + content[results_close:]

added_count = sum(len(v) for v in seasons.values())
print(f"  Added {added_count} entries to RESULTS")
for sn, ids in seasons.items():
    print(f"    {sn}: {len(ids)} entries")

# ── Step 5: Validate and write ─────────────────────────────────────────────────
print("\n=== Step 5: Writing build_tracker.py ===")

# Quick sanity check: count WAR_BLOCK entries in new content
new_entry_count = len(re.findall(r'\("\w+","[^"]+","[^"]+","[^"]+","""', content))
print(f"  WAR_BLOCKS entries: {new_entry_count} (was 39)")

with open('build_tracker.py', 'w') as f:
    f.write(content)

print("\n✅ Done! build_tracker.py updated.")
print(f"  Total WAR_BLOCK entries: {new_entry_count}")
print(f"  CWL entries upgraded to v2: {upgraded}")
print(f"  New CWL entries inserted: {inserted}")
print(f"  RESULTS entries added: {added_count}")
print("\n⚠️  NOTE: New CWL RESULTS default to 'W' — review Dec/Jan/Feb/Mar rounds for accuracy.")
