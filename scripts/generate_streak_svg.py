#!/usr/bin/env python3
"""
Fetch GitHub contribution calendar SVG and generate a compact streak SVG.
Saves output to provided file path.
"""
import argparse
import requests
from lxml import etree
from datetime import datetime


def fetch_calendar(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text


def parse_counts(svg_text: str):
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(svg_text.encode("utf-8"), parser=parser)
    rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
    data = []
    for r in rects:
        date = r.get('data-date')
        count = r.get('data-count')
        if date and count is not None:
            data.append((date, int(count)))
    data.sort(key=lambda x: x[0])
    return data


def compute_current_streak(data):
    if not data:
        return 0
    streak = 0
    # Iterate from most recent day backward
    for date, count in reversed(data):
        if count > 0:
            streak += 1
        else:
            break
    return streak


def total_contributions(data):
    return sum(c for _, c in data)


def render_svg(streak: int, total: int, username: str) -> str:
    now = datetime.utcnow().strftime('%Y-%m-%d')
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="360" height="90" viewBox="0 0 360 90">
  <rect width="360" height="90" rx="8" fill="#0D1117" stroke="#2d3748"/>
  <text x="24" y="30" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#79D1FF">{username} — Contributions</text>
  <text x="24" y="56" font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#ffffff">Current Streak: <tspan fill="#7CFFB2">{streak}</tspan></text>
  <text x="24" y="78" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#9aa4b2">Total: {total} • Updated: {now} UTC</text>
</svg>
'''
    return svg


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--username', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    try:
        svg_text = fetch_calendar(args.username)
        data = parse_counts(svg_text)
        streak = compute_current_streak(data)
        total = total_contributions(data)
        out_svg = render_svg(streak, total, args.username)
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(out_svg)
        print(f'Wrote {args.out} (streak={streak}, total={total})')
    except Exception as e:
        print('Error generating streak SVG:', e)
        raise


if __name__ == '__main__':
    main()
