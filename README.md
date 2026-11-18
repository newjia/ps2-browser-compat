# PS2 browser-emulator compatibility data

A plain CSV/JSON list of PS2 disc versions that the Play! emulator project's compatibility tracker marks **Playable** or **In-game**. It is the data behind the human-readable table at https://nostalith.com/games/ps2/compatibility/.

This repository contains no game files, disc images or BIOS files, and gives no instructions for obtaining them.

## Data

- `data/compat.csv`, `data/compat.json`: 2,284 rows (1,304 Playable, 980 In-game), one per tracker report. Data read on 2026-11-18.
- Source: https://github.com/jpd002/Play-Compatibility, open issues carrying the label `state-playable` or `state-ingame`. Homebrew and arcade-board entries (`type-*` labels) are left out. Reports with an `intro`, `loadable` or `nothing` status are not included.

| Field | Meaning |
| --- | --- |
| `title` | Issue title with the leading `[disc ID]` removed |
| `serial` | Disc ID from the issue title, e.g. `SLUS-21258`. Empty for 4 reports whose title has no ID |
| `region` | Derived by us from the serial prefix: SLUS/SCUS = NTSC-U; SLES/SCES/SCED = PAL; SLPM/SLPS/SCPS/SCPM/SPLM/PBPX = NTSC-J; SLKA/SCKA = NTSC-K. Empty for other prefixes |
| `status` | `Playable` or `In-game`, from the tracker label |
| `issue_labels` | Technical `issue-*` labels set on the report (e.g. `idledetection`, `memorycard`), `|`-separated, prefix removed |
| `report_url`, `issue_number` | Link to the tracker report, where the tester's notes and test date can be read |
| `read_date` | Date we read the tracker |

## Status definitions

Quoted from the tracker README (https://github.com/jpd002/Play-Compatibility#game-statuses):

- **state-playable**: "means that the game is fully playable."
- **state-ingame**: "means somewhat playable past title screens (including with graphics bugs, crashes, saving, loading and other major problems)."

## Method

`scripts/build.py` reads the tracker through the public GitHub API and keeps only the fields above. Issue bodies and comments are not copied. Run `python3 scripts/build.py`; set `GITHUB_TOKEN` in the environment only if you hit the rate limit.

## Limitations

- The tracker covers Play! on all platforms (desktop and mobile builds). The browser version of Play! is described by the project as an experiment, so a game listed as Playable may run slower or with more problems in a browser.
- Statuses are tester-reported and can be out of date; the report page has the details. Check the tracker for newer reports.
- This is a snapshot of one date, not a live feed.

## Credits and license

Compatibility reports are by the Play! project's testers and maintainers: https://github.com/jpd002/Play-Compatibility. Play! is by Jean-Philip Desjardins and contributors: https://github.com/jpd002/Play-.

Our compilation of the data: CC BY 4.0, see `LICENSE` and `NOTICE.md`. The script in `scripts/`: MIT, see `LICENSE-CODE`. Please cite https://nostalith.com/games/ps2/compatibility/.
