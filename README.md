# GitHub Activity Generator

A Python tool that fills your GitHub contribution graph by creating backdated commits with realistic patterns.

---

## Features

- 🗓️ **Custom date ranges** — target any time period
- 📈 **4 frequency modes** — sparse, moderate, active, daily
- 📅 **Weekday-only mode** — simulate a realistic work schedule
- 🔀 **Randomized commit times** — natural-looking activity spread throughout the day
- 💬 **Realistic commit messages** — chosen from a curated set of common messages
- 🚀 **Auto push to GitHub** — optionally push generated commits straight to remote
- 🔧 **Auto repo initialization** — creates the repo if it doesn't exist

---

## Requirements

- Python 3.10+
- Git installed and configured (`git config --global user.name` and `user.email`)

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/github-activity-generator.git
cd github-activity-generator
```

No external dependencies — uses only the Python standard library.

---

## Usage

### Basic usage (last 1 year, moderate frequency)

```bash
python contribute.py
```

This creates an `./activity-repo` folder, initializes a git repo inside it, and fills it with commits.

### Custom date range

```bash
python contribute.py --start 2024-01-01 --end 2024-12-31
```

### Frequency modes

| Mode       | Description                                  |
|------------|----------------------------------------------|
| `sparse`   | ~20% chance per day, 1–2 commits             |
| `moderate` | ~55% chance per day, 1–4 commits *(default)* |
| `active`   | ~80% chance per day, up to max commits       |
| `daily`    | Commits every single day                     |

```bash
python contribute.py --frequency active --max-per-day 8
```

### Weekdays only

```bash
python contribute.py --weekdays
```

### Push to GitHub

```bash
# Initialize with your remote URL and push
python contribute.py \
  --repo ./my-repo \
  --remote https://github.com/YOUR_USERNAME/REPO_NAME.git \
  --push
```

---

## All options

```
usage: contribute.py [-h] [--repo REPO] [--start START] [--end END]
                     [--frequency {sparse,moderate,active,daily}]
                     [--max-per-day MAX_PER_DAY] [--weekdays] [--push]
                     [--remote REMOTE] [--no-init]

options:
  -h, --help            Show this help message and exit
  --repo, -r            Path to the git repository (default: ./activity-repo)
  --start, -s           Start date YYYY-MM-DD (default: 1 year ago)
  --end, -e             End date YYYY-MM-DD (default: today)
  --frequency, -f       Commit frequency: sparse | moderate | active | daily
  --max-per-day, -m     Maximum commits per day (default: 5)
  --weekdays            Only commit on weekdays (Mon–Fri)
  --push, -p            Push to remote after generating
  --remote              Remote repository URL
  --no-init             Don't auto-initialize repo if missing
```

---

## How it works

1. Creates or uses an existing git repository at the target path
2. Generates a list of commit timestamps based on your frequency/date settings
3. For each timestamp, appends a line to `activity.log` and commits with `GIT_AUTHOR_DATE` / `GIT_COMMITTER_DATE` set to that past date
4. GitHub counts these as contributions when pushed to a public repository

> **Note:** GitHub only counts contributions to the **default branch** of a repository. Make sure your remote repo's default branch is `main` or `master`.

---

## Example output

```
=======================================================
  GitHub Activity Generator
=======================================================
  Repository : /home/user/my-repo
  Date range : 2024-06-07 → 2025-06-07
  Frequency  : moderate
  Max/day    : 5
  Weekdays   : all days
=======================================================

  ✓ Repository initialized

  Generating 412 commits...

  [████████████████████████████████████████] 412/412

  ✓ Created 412 commits successfully!

  Pushing to remote...
  ✓ Pushed to remote successfully!

=======================================================
  Done! Check your GitHub profile in a few minutes.
=======================================================
```

---

## License

MIT
