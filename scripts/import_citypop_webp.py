#!/usr/bin/env python3
"""Safely switch Encounter Japan draft artwork from SVG to approved optimized WebP assets.

Place assets/editorial/tokyo-night.webp, bookshop-day.webp and rooftop-lounge.webp
in the checked-out repository first. Run once without --apply for validation.
This never merges, pushes, or deploys.
"""
import argparse
import subprocess
from pathlib import Path

SWAPS = {
    'assets/editorial/night-street.svg': 'assets/editorial/tokyo-night.webp',
    'assets/editorial/day-bookshop.svg': 'assets/editorial/bookshop-day.webp',
    'assets/editorial/rooftop-citypop.svg': 'assets/editorial/rooftop-lounge.webp',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    repo = args.repo.resolve()
    page = repo / 'tokyo-guide_2.html'
    if not page.is_file():
        raise SystemExit('Missing repository HTML: '+str(page))
    for target in SWAPS.values():
        if not (repo/target).is_file():
            raise SystemExit('Missing optimized artwork: '+str(repo/target))
    if args.apply:
        branch = subprocess.run(['git', '-C', str(repo), 'branch', '--show-current'],
                                capture_output=True, text=True, check=True).stdout.strip()
        if not branch or branch in ('main', 'master'):
            raise SystemExit('Refusing to modify main, master or detached HEAD')
    original = page.read_text(encoding='utf-8')
    before = (original.count('name:"'), original.count('https://www.google.com/maps/'))
    if before != (526, 526):
        raise SystemExit('526-record invariant failed before: '+repr(before))
    changed = original
    for old, new in SWAPS.items():
        if old not in changed and new not in changed:
            raise SystemExit('Expected image reference absent: '+old)
        changed = changed.replace(old, new)
    after = (changed.count('name:"'), changed.count('https://www.google.com/maps/'))
    if before != after:
        raise SystemExit('Place records or Maps links changed')
    if args.apply:
        page.write_text(changed, encoding='utf-8')
        print('Updated image references. Run browser QA; no commit/push/merge/deploy.')
    else:
        print('Dry run succeeded; 526 entries/Maps links preserved. Use --apply to write.')


if __name__ == '__main__':
    main()
