#!/usr/bin/env python3
"""
GitHub Activity Generator
Generates realistic commit history by making backdated commits to a repository.
"""

import argparse
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Commit message templates for realistic activity
COMMIT_MESSAGES = [
    "Update README.md",
    "Fix typo in documentation",
    "Refactor utility functions",
    "Add error handling",
    "Improve performance",
    "Clean up code",
    "Fix edge case in validation",
    "Update dependencies",
    "Add unit tests",
    "Minor bug fix",
    "Improve logging",
    "Add input validation",
    "Code cleanup",
    "Fix formatting issues",
    "Update configuration",
    "Optimize query performance",
    "Add documentation comments",
    "Resolve merge conflict",
    "Hotfix for production issue",
    "Implement feature request",
    "Update .gitignore",
    "Refactor for readability",
    "Add type hints",
    "Remove unused imports",
    "Improve error messages",
    "Fix broken link in docs",
    "Update changelog",
    "Bump version number",
    "Add missing semicolons",
    "Revert accidental change",
]


def run_command(cmd: list[str], cwd: str = None) -> tuple[int, str, str]:
    """Run a shell command and return returncode, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_git_repo(path: str) -> bool:
    """Check if the given path is a git repository."""
    code, _, _ = run_command(["git", "rev-parse", "--git-dir"], cwd=path)
    return code == 0


def init_git_repo(path: str, remote_url: str = None) -> bool:
    """Initialize a new git repository."""
    os.makedirs(path, exist_ok=True)

    code, _, err = run_command(["git", "init"], cwd=path)
    if code != 0:
        print(f"  ✗ Failed to init repo: {err}")
        return False

    # Create initial README
    readme_path = Path(path) / "README.md"
    if not readme_path.exists():
        readme_path.write_text("# GitHub Activity Generator\n\nAutomatically generated commit history.\n")

    # Initial commit
    run_command(["git", "add", "."], cwd=path)
    run_command(["git", "commit", "-m", "Initial commit"], cwd=path)

    if remote_url:
        run_command(["git", "remote", "add", "origin", remote_url], cwd=path)
        print(f"  ✓ Remote set to: {remote_url}")

    return True


def make_commit(repo_path: str, date: datetime, message: str = None) -> bool:
    """Make a single commit on the specified date."""
    if message is None:
        message = random.choice(COMMIT_MESSAGES)

    # Update the contribution file with a small change
    contrib_file = Path(repo_path) / "activity.log"
    with open(contrib_file, "a") as f:
        f.write(f"{date.isoformat()} - {message}\n")

    # Stage the file
    code, _, err = run_command(["git", "add", "activity.log"], cwd=repo_path)
    if code != 0:
        return False

    # Commit with the backdated timestamp
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_path,
        env=env,
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def generate_dates(
    start_date: datetime,
    end_date: datetime,
    frequency: str,
    max_per_day: int,
    weekdays_only: bool
) -> list[datetime]:
    """Generate a list of commit dates based on the given parameters."""
    dates = []
    current = start_date

    while current <= end_date:
        # Skip weekends if requested
        if weekdays_only and current.weekday() >= 5:
            current += timedelta(days=1)
            continue

        # Determine number of commits for this day
        if frequency == "sparse":
            # ~20% chance of committing on any given day
            if random.random() < 0.20:
                count = random.randint(1, min(2, max_per_day))
            else:
                count = 0
        elif frequency == "moderate":
            # ~55% chance of committing
            if random.random() < 0.55:
                count = random.randint(1, min(max_per_day, 4))
            else:
                count = 0
        elif frequency == "active":
            # ~80% chance, more commits per day
            if random.random() < 0.80:
                count = random.randint(1, max_per_day)
            else:
                count = 0
        else:  # daily
            count = random.randint(1, max_per_day)

        # Add commits with random times throughout the day
        for _ in range(count):
            hour = random.randint(9, 22)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            commit_date = current.replace(hour=hour, minute=minute, second=second)
            dates.append(commit_date)

        current += timedelta(days=1)

    return sorted(dates)


def push_to_remote(repo_path: str, branch: str = "main") -> bool:
    """Push commits to the remote repository."""
    # Try to set upstream and push
    code, _, err = run_command(
        ["git", "push", "-u", "origin", branch, "--force"],
        cwd=repo_path
    )
    if code != 0:
        # Try master branch as fallback
        code, _, err = run_command(
            ["git", "push", "-u", "origin", "master", "--force"],
            cwd=repo_path
        )
    return code == 0


def generate_activity(
    repo_path: str,
    start_date: datetime,
    end_date: datetime,
    frequency: str = "moderate",
    max_per_day: int = 5,
    weekdays_only: bool = False,
    push: bool = False,
    remote_url: str = None,
    no_init: bool = False,
) -> int:
    """
    Main function to generate GitHub activity.
    Returns the number of commits made.
    """
    repo_path = os.path.abspath(repo_path)

    print(f"\n{'='*55}")
    print(f"  GitHub Activity Generator")
    print(f"{'='*55}")
    print(f"  Repository : {repo_path}")
    print(f"  Date range : {start_date.date()} → {end_date.date()}")
    print(f"  Frequency  : {frequency}")
    print(f"  Max/day    : {max_per_day}")
    print(f"  Weekdays   : {'only' if weekdays_only else 'all days'}")
    print(f"{'='*55}\n")

    # Initialize or verify repo
    if not check_git_repo(repo_path):
        if no_init:
            print("✗ Not a git repository. Use --no-init=false to auto-initialize.")
            return 0
        print("  Initializing git repository...")
        if not init_git_repo(repo_path, remote_url):
            return 0
        print("  ✓ Repository initialized\n")
    else:
        print("  ✓ Git repository found\n")
        if remote_url:
            run_command(["git", "remote", "set-url", "origin", remote_url], cwd=repo_path)

    # Generate commit dates
    dates = generate_dates(start_date, end_date, frequency, max_per_day, weekdays_only)

    if not dates:
        print("  ✗ No commits to generate with current settings.")
        return 0

    print(f"  Generating {len(dates)} commits...\n")

    # Make commits
    success_count = 0
    total = len(dates)
    bar_width = 40

    for i, date in enumerate(dates):
        if make_commit(repo_path, date):
            success_count += 1

        # Progress bar
        progress = (i + 1) / total
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"\r  [{bar}] {i+1}/{total}", end="", flush=True)

    print(f"\n\n  ✓ Created {success_count} commits successfully!\n")

    # Push if requested
    if push:
        print("  Pushing to remote...")
        if push_to_remote(repo_path):
            print("  ✓ Pushed to remote successfully!\n")
        else:
            print("  ✗ Push failed. Try: git push origin main --force\n")

    print(f"{'='*55}")
    print(f"  Done! Check your GitHub profile in a few minutes.")
    print(f"{'='*55}\n")

    return success_count


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate GitHub activity by creating backdated commits.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate activity for the past year (moderate frequency)
  python contribute.py --repo ./my-repo

  # Custom date range with high activity
  python contribute.py --repo ./my-repo --start 2025-01-01 --end 2025-12-31 --frequency active

  # Sparse activity, weekdays only, push to GitHub
  python contribute.py --repo ./my-repo --frequency sparse --weekdays --push

  # Use an existing GitHub repo URL
  python contribute.py --repo ./my-repo --remote https://github.com/user/repo.git --push
        """
    )

    parser.add_argument(
        "--repo", "-r",
        default="./activity-repo",
        help="Path to the git repository (default: ./activity-repo)"
    )
    parser.add_argument(
        "--start", "-s",
        help="Start date in YYYY-MM-DD format (default: 1 year ago)"
    )
    parser.add_argument(
        "--end", "-e",
        help="End date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--frequency", "-f",
        choices=["sparse", "moderate", "active", "daily"],
        default="moderate",
        help="Commit frequency pattern (default: moderate)"
    )
    parser.add_argument(
        "--max-per-day", "-m",
        type=int,
        default=5,
        help="Maximum commits per day (default: 5)"
    )
    parser.add_argument(
        "--weekdays",
        action="store_true",
        help="Only commit on weekdays (Mon-Fri)"
    )
    parser.add_argument(
        "--push", "-p",
        action="store_true",
        help="Push commits to remote after generating"
    )
    parser.add_argument(
        "--remote",
        help="Remote repository URL (e.g. https://github.com/user/repo.git)"
    )
    parser.add_argument(
        "--no-init",
        action="store_true",
        help="Do not initialize a new repo if one doesn't exist"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Parse dates
    end_date = datetime.now().replace(hour=23, minute=59, second=59)
    start_date = (end_date - timedelta(days=365)).replace(hour=0, minute=0, second=0)

    if args.end:
        try:
            end_date = datetime.strptime(args.end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            print(f"✗ Invalid end date format: {args.end}. Use YYYY-MM-DD.")
            sys.exit(1)

    if args.start:
        try:
            start_date = datetime.strptime(args.start, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        except ValueError:
            print(f"✗ Invalid start date format: {args.start}. Use YYYY-MM-DD.")
            sys.exit(1)

    if start_date >= end_date:
        print("✗ Start date must be before end date.")
        sys.exit(1)

    if args.max_per_day < 1 or args.max_per_day > 50:
        print("✗ max-per-day must be between 1 and 50.")
        sys.exit(1)

    generate_activity(
        repo_path=args.repo,
        start_date=start_date,
        end_date=end_date,
        frequency=args.frequency,
        max_per_day=args.max_per_day,
        weekdays_only=args.weekdays,
        push=args.push,
        remote_url=args.remote,
        no_init=args.no_init,
    )


if __name__ == "__main__":
    main()
