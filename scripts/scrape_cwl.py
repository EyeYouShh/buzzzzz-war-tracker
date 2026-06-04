#!/usr/bin/env python3
"""Scrape CWL war pages from ClashSpot using only stdlib."""
import urllib.request, re, json, time, sys
from html.parser import HTMLParser

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

CWL_URLS = [
    # May 2026
    ('2026-05', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-05/war/8LVUPY0R9/c/2GGL80JL0'),
    ('2026-05', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-05/war/8Q0020RCC/c/2GGL80JL0'),
    ('2026-05', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-05/war/8Q0882R82/c/2GGL80JL0'),
    ('2026-05', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-05/war/8Q0P0CYLR/c/2GGL80JL0'),
    ('2026-05', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-05/war/8Q0L0VR82/c/2GGL80JL0'),
    ('2026-05', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-05/war/8Q0G02CGY/c/2GGL80JL0'),
    ('2026-05', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-05/war/8Q0J0022Q/c/2GGL80JL0'),
    # April 2026
    ('2026-04', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-04/war/8LQCG02G9/c/2GGL80JL0'),
    ('2026-04', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-04/war/8LQUVPLJ9/c/2GGL80JL0'),
    ('2026-04', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-04/war/8LG0VRGUQ/c/2GGL80JL0'),
    ('2026-04', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-04/war/8LG98L2PC/c/2GGL80JL0'),
    ('2026-04', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-04/war/8LGY9RLGQ/c/2GGL80JL0'),
    ('2026-04', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-04/war/8LGQYCQQ2/c/2GGL80JL0'),
    ('2026-04', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-04/war/8LGRLVYU9/c/2GGL80JL0'),
    # March 2026
    ('2026-03', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-03/war/8LU2822CG/c/2GGL80JL0'),
    ('2026-03', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-03/war/8LU9QV89P/c/2GGL80JL0'),
    ('2026-03', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-03/war/8LUL2CUV0/c/2GGL80JL0'),
    ('2026-03', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-03/war/8LUGGL2RU/c/2GGL80JL0'),
    ('2026-03', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-03/war/8LUC82QYP/c/2GGL80JL0'),
    ('2026-03', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-03/war/8LUVGV9C0/c/2GGL80JL0'),
    ('2026-03', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-03/war/8LV88URGJ/c/2GGL80JL0'),
    # February 2026
    ('2026-02', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-02/war/8GRLVCCUR/c/2GGL80JL0'),
    ('2026-02', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-02/war/8GRGG9Q29/c/2GGL80JL0'),
    ('2026-02', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-02/war/8GRJV2PVQ/c/2GGL80JL0'),
    ('2026-02', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-02/war/8GRVLY9G2/c/2GGL80JL0'),
    ('2026-02', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-02/war/8GJ2CJLGV/c/2GGL80JL0'),
    ('2026-02', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-02/war/8GJPY8YVC/c/2GGL80JL0'),
    ('2026-02', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-02/war/8GJLRCP0V/c/2GGL80JL0'),
    # January 2026
    ('2026-01', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-01/war/8YCYRJ88Q/c/2GGL80JL0'),
    ('2026-01', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-01/war/8YCQR0QVR/c/2GGL80JL0'),
    ('2026-01', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-01/war/8YCJ8YG9R/c/2GGL80JL0'),
    ('2026-01', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-01/war/8YCUGRVLC/c/2GGL80JL0'),
    ('2026-01', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-01/war/8YU20V90Q/c/2GGL80JL0'),
    ('2026-01', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-01/war/8YU9Q8QUQ/c/2GGL80JL0'),
    ('2026-01', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2026-01/war/8YUL00G92/c/2GGL80JL0'),
    # December 2025
    ('2025-12', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2025-12/war/8QJJURPPC/c/2GGL80JL0'),
    ('2025-12', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2025-12/war/8QJVLPVV2/c/2GGL80JL0'),
    ('2025-12', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2025-12/war/8QC2VJ8CR/c/2GGL80JL0'),
    ('2025-12', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2025-12/war/8QCPQ2JVY/c/2GGL80JL0'),
    ('2025-12', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2025-12/war/8QCQ0VUQ2/c/2GGL80JL0'),
    ('2025-12', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2025-12/war/8QCRGJC22/c/2GGL80JL0'),
    ('2025-12', 'https://clashspot.net/en/clan/2GGL80JL0/clan-war-leagues/2025-12/war/8QCCR22LC/c/2GGL80JL0'),
]

def html_unescape(s):
    return (s.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
             .replace('&quot;','"').replace('&#39;',"'").replace('&nbsp;',' ')
             .replace('&#x27;',"'").replace('&#x2F;','/'))

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

def extract_war(html, url, season):
    war_id = re.search(r'/war/([^/]+)/', url)
    war_id = war_id.group(1) if war_id else 'UNKNOWN'

    # Title → opponent
    title_m = re.search(r'<title>([^<]+)</title>', html)
    title = html_unescape(title_m.group(1)) if title_m else ''
    opp_m = re.search(r'versus (.+?) \(#[^)]+\)', title)
    opponent = opp_m.group(1) if opp_m else 'Unknown'

    # Dates from page text
    end_m  = re.search(r'ENDED ON\s*</[^>]+>\s*<[^>]+>\s*([^<]+)', html)
    start_m = re.search(r'STARTED ON\s*</[^>]+>\s*<[^>]+>\s*([^<]+)', html)
    end_date = ''
    if end_m:
        raw = html_unescape(end_m.group(1)).strip()
        dm = re.search(r'(\d+/\d+/\d+)', raw)
        if dm: end_date = dm.group(1)
    if not end_date and start_m:
        raw = html_unescape(start_m.group(1)).strip()
        dm = re.search(r'(\d+/\d+/\d+)', raw)
        if dm: end_date = dm.group(1)

    # ── Parse member blocks: class="members-position ..."
    # Each block: find first player link → our member name, pos, tag, TH
    our_members = {}  # name → {pos, tag, th}
    blocks = re.findall(r'class="members-position[^"]*"[^>]*>(.*?)(?=class="members-position|<div class="war-details|$)', html, re.DOTALL)
    for block in blocks:
        # First player link
        link_m = re.search(r'href="/en/player/([A-Z0-9]+)/view"[^>]*title="([^"]+)"', block, re.I)
        if not link_m:
            continue
        raw_tag = link_m.group(1).upper()
        tag = '#' + raw_tag
        title_attr = html_unescape(link_m.group(2))
        th_m = re.search(r'TH\s*(\d+)', title_attr, re.I)
        th = int(th_m.group(1)) if th_m else 0
        name_m = re.search(r'title="([^"]+) - #[A-Z0-9]+ - TH', title_attr, re.I)
        if not name_m:
            # fallback: name is first part before ' - '
            name_m2 = re.search(r'^(.+?) - #', title_attr)
            name = name_m2.group(1).strip() if name_m2 else title_attr.split(' - ')[0].strip()
        else:
            name = name_m.group(1).strip()
        name = html_unescape(name)
        # Position: first number in block text (strip tags)
        text = re.sub(r'<[^>]+>', ' ', block)
        pos_m = re.search(r'^\s*(\d+)', text.strip())
        pos = int(pos_m.group(1)) if pos_m else 0
        if name and pos:
            our_members[name] = {'pos': pos, 'tag': tag, 'th': th}

    # ── Enemy positions from member block text: lines after our member
    # Pattern: digit-only line followed by name not in our_members
    enemy_pos = {}
    for block in blocks:
        text = re.sub(r'<[^>]+>', '\n', block)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for i in range(2, len(lines)-1):
            if re.match(r'^\d+$', lines[i]) and lines[i+1] and lines[i+1] not in our_members:
                ename = html_unescape(lines[i+1])
                if ename not in enemy_pos:
                    enemy_pos[ename] = int(lines[i])

    # ── Attack table: find tbody rows after "Stars" header
    # Stars class pattern: stars-N
    attack_rows = []
    # Find the attack log table (has Order/Attacker/Defender/Stars/Destruction headers)
    table_m = re.search(r'<th[^>]*>\s*Order\s*</th>.*?<tbody>(.*?)</tbody>', html, re.DOTALL)
    if table_m:
        tbody = table_m.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody, re.DOTALL)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) < 6:
                continue
            # Cell 1 = attacker, Cell 2 = defender, Cell 4 = stars
            def extract_player(cell):
                lm = re.search(r'title="([^"]+) - #[A-Z0-9]+ - TH', cell, re.I)
                if lm: return html_unescape(lm.group(1).strip())
                nm = re.search(r'class="[^"]*player-identity[^"]*"[^>]*>\s*<[^>]*>\s*([^<]+)', cell, re.DOTALL)
                if nm: return html_unescape(nm.group(1).strip())
                return None
            def extract_th(cell):
                tm2 = re.search(r'TH\s*(\d+)', cell, re.I)
                return int(tm2.group(1)) if tm2 else 0
            def extract_stars(cell):
                sm2 = re.search(r'class="stars stars-(\d)', cell)
                return int(sm2.group(1)) if sm2 else 0

            attacker = extract_player(cells[1])
            defender = extract_player(cells[2])
            stars = extract_stars(cells[4])
            def_th = extract_th(cells[2])
            if attacker and defender:
                attack_rows.append({'attacker': attacker, 'defender': defender, 'stars': stars, 'defTH': def_th})

    # ── Filter to our attacks, compute net stars
    best = {}
    our_attacks = []
    for a in attack_rows:
        if a['attacker'] not in our_members:
            continue
        def_pos = enemy_pos.get(a['defender'], '?')
        prev = best.get(def_pos, 0)
        net = max(0, a['stars'] - prev)
        best[def_pos] = max(prev, a['stars'])
        our_attacks.append({**a, 'defPos': def_pos, 'net': net})

    # ── Group by member
    by_member = {n: [] for n in our_members}
    for a in our_attacks:
        if a['attacker'] in by_member:
            by_member[a['attacker']].append(a)

    # ── Build v2 lines
    size = len(our_members)
    lines = []
    for name, m in sorted(our_members.items(), key=lambda x: x[1]['pos']):
        atks = by_member.get(name, [])
        used = len(atks)
        raw_s = sum(a['stars'] for a in atks)
        net_s = sum(a['net'] for a in atks)
        atk_str = ','.join(f"{a['defPos']}:{a['stars']}:{a['net']}:{a['defTH']}" for a in atks)
        lines.append(f"{m['tag']}|{name}|{m['pos']}|{m['th']}|{used}|{raw_s}|{net_s}|{atk_str}")

    block = f'("{war_id}","{end_date}","{opponent}","{size}v{size}","""\n' + '\n'.join(lines) + '\n""", False, True),'
    missing = list({a['defender'] for a in our_attacks if enemy_pos.get(a['defender']) is None or a['defPos'] == '?'})

    return {
        'warId': war_id, 'season': season, 'endDate': end_date,
        'opponent': opponent, 'size': size,
        'ourAttacks': len(our_attacks), 'missing': missing,
        'block': block
    }

def main():
    output_path = '/Users/aayushpatel/Documents/Computer Brain/Claude Cowork/PROJECTS/CoC/scraped_cwl.json'
    results = []
    for i, (season, url) in enumerate(CWL_URLS):
        war_id = re.search(r'/war/([^/]+)/', url).group(1)
        print(f"[{i+1}/{len(CWL_URLS)}] {season} {war_id} ...", end=' ', flush=True)
        try:
            html = fetch(url)
            data = extract_war(html, url, season)
            results.append(data)
            print(f"OK — {data['opponent']} ({data['ourAttacks']} atks, {len(data['missing'])} missing)")
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({'warId': war_id, 'season': season, 'url': url, 'error': str(e)})
        # Save every 5
        if (i+1) % 5 == 0:
            with open(output_path, 'w') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        time.sleep(0.3)  # polite delay

    with open(output_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    good = [r for r in results if 'block' in r]
    errors = [r for r in results if 'error' in r]
    print(f"\nDone: {len(good)} OK, {len(errors)} errors")
    if errors:
        for e in errors: print(f"  ERROR: {e}")

if __name__ == '__main__':
    main()
