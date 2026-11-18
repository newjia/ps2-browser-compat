#!/usr/bin/env python3
"""Regenerate data/compat.csv and data/compat.json from the Play! compatibility tracker.

Reads open issues of jpd002/Play-Compatibility labeled state-playable or state-ingame
through the public GitHub REST API. Only metadata is kept: issue number, title, disc ID
(serial), region (derived from the serial prefix), status label, project issue-* labels.
Issue bodies and comments are never read into the output.

Unauthenticated use is enough (~30 calls, limit 60/hour). To raise the limit, set the
GITHUB_TOKEN environment variable; never put a token in a file.
Usage: python3 scripts/build.py [--out DIR]   (default DIR = ../data)
"""
import argparse, csv, datetime, json, os, pathlib, re, urllib.request

REPO = 'jpd002/Play-Compatibility'
API = 'https://api.github.com'
REGION = {'SLUS': 'NTSC-U', 'SCUS': 'NTSC-U', 'SLES': 'PAL', 'SCES': 'PAL', 'SCED': 'PAL',
          'SLPM': 'NTSC-J', 'SLPS': 'NTSC-J', 'SCPS': 'NTSC-J', 'SCPM': 'NTSC-J', 'SPLM': 'NTSC-J',
          'PBPX': 'NTSC-J', 'SLKA': 'NTSC-K', 'SCKA': 'NTSC-K'}
STATUS = {'state-playable': 'Playable', 'state-ingame': 'In-game'}
FIELDS = ['title', 'serial', 'region', 'status', 'issue_labels', 'report_url', 'issue_number', 'read_date']


def get(url):
    h = {'User-Agent': 'ps2-browser-compat-build', 'Accept': 'application/vnd.github+json'}
    if os.environ.get('GITHUB_TOKEN'):
        h['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60))


def fetch():
    rows, seen = [], set()
    for label, status in STATUS.items():
        total = get(f'{API}/search/issues?q=repo:{REPO}+label:{label}+state:open&per_page=1')['total_count']
        got = 0
        # list API stops at 1,000 results: read newest-first, then oldest-first
        for direction in ('desc', 'asc'):
            for page in range(1, 11):
                if got >= total:
                    break
                batch = get(f'{API}/repos/{REPO}/issues?labels={label}&state=open&per_page=100&page={page}&direction={direction}')
                for i in batch:
                    if i['number'] in seen or 'pull_request' in i:
                        continue
                    labels = [l['name'] for l in i['labels']]
                    if any(l.startswith('type-') for l in labels):  # homebrew / arcade boards
                        continue
                    seen.add(i['number']); got += 1
                    m = re.match(r'\s*\[([A-Z]{4}-\d{5})\]\s*(.+)', i['title'])
                    serial = m.group(1) if m else ''
                    rows.append({'title': (m.group(2) if m else i['title']).strip(), 'serial': serial,
                                 'region': REGION.get(serial[:4], ''), 'status': status,
                                 'issue_labels': [l[6:] for l in labels if l.startswith('issue-')],
                                 'report_url': f'https://github.com/{REPO}/issues/{i["number"]}',
                                 'issue_number': i['number']})
                if len(batch) < 100:
                    break
        print(label, 'search total', total, 'kept', got)
    return rows


def write(rows, out, read_date):
    rows.sort(key=lambda r: (r['title'].lower(), r['serial']))
    for r in rows:
        r['read_date'] = read_date
    out.mkdir(parents=True, exist_ok=True)
    with open(out / 'compat.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, FIELDS, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({**r, 'issue_labels': '|'.join(r['issue_labels'])})
    (out / 'compat.json').write_text(json.dumps(
        {'source': f'https://github.com/{REPO}', 'read_date': read_date, 'count': len(rows),
         'rows': [{k: r[k] for k in FIELDS} for r in rows]}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('wrote', len(rows), 'rows ->', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(pathlib.Path(__file__).resolve().parent.parent / 'data'))
    a = ap.parse_args()
    write(fetch(), pathlib.Path(a.out), datetime.date.today().isoformat())
