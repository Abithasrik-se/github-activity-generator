"""
Tests for GitHub Activity Generator
"""

import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

from contribute import (
    check_git_repo,
    generate_dates,
    init_git_repo,
    make_commit,
    run_command,
)


class TestRunCommand(unittest.TestCase):
    def test_basic_command(self):
        code, stdout, _ = run_command(["echo", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "hello")

    def test_failing_command(self):
        code, _, _ = run_command(["git", "rev-parse", "--git-dir"], cwd="/tmp")
        self.assertNotEqual(code, 0)


class TestGitRepo(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_not_a_repo(self):
        self.assertFalse(check_git_repo(self.tmpdir))

    def test_init_and_check(self):
        result = init_git_repo(self.tmpdir)
        self.assertTrue(result)
        self.assertTrue(check_git_repo(self.tmpdir))

    def test_init_creates_readme(self):
        init_git_repo(self.tmpdir)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "README.md")))


class TestGenerateDates(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2024, 1, 1)
        self.end = datetime(2024, 1, 31)

    def test_daily_generates_commits_every_day(self):
        dates = generate_dates(self.start, self.end, "daily", 3, False)
        self.assertGreater(len(dates), 0)
        # Daily should have at least 1 commit per day on average
        days = (self.end - self.start).days + 1
        self.assertGreaterEqual(len(dates), days)

    def test_weekdays_only(self):
        dates = generate_dates(self.start, self.end, "daily", 1, weekdays_only=True)
        for d in dates:
            self.assertLess(d.weekday(), 5, f"{d} is a weekend day")

    def test_dates_are_sorted(self):
        dates = generate_dates(self.start, self.end, "moderate", 3, False)
        self.assertEqual(dates, sorted(dates))

    def test_dates_within_range(self):
        dates = generate_dates(self.start, self.end, "active", 5, False)
        for d in dates:
            self.assertGreaterEqual(d.date(), self.start.date())
            self.assertLessEqual(d.date(), self.end.date())

    def test_max_per_day_respected(self):
        max_per_day = 2
        dates = generate_dates(self.start, self.end, "daily", max_per_day, False)
        # Count commits per day
        from collections import Counter
        day_counts = Counter(d.date() for d in dates)
        for day, count in day_counts.items():
            self.assertLessEqual(count, max_per_day, f"{day} has {count} commits > {max_per_day}")

    def test_sparse_has_fewer_commits_than_active(self):
        # Run multiple times and compare averages to reduce flakiness
        sparse_counts = []
        active_counts = []
        for _ in range(5):
            sparse = generate_dates(self.start, self.end, "sparse", 5, False)
            active = generate_dates(self.start, self.end, "active", 5, False)
            sparse_counts.append(len(sparse))
            active_counts.append(len(active))
        self.assertLess(sum(sparse_counts) / 5, sum(active_counts) / 5)


class TestMakeCommit(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Configure git for testing
        run_command(["git", "config", "user.email", "test@test.com"], cwd=self.tmpdir)
        run_command(["git", "config", "user.name", "Test User"], cwd=self.tmpdir)
        init_git_repo(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_commit_creates_file(self):
        date = datetime(2024, 6, 1, 10, 0, 0)
        result = make_commit(self.tmpdir, date, "Test commit")
        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "activity.log")))

    def test_commit_has_correct_date(self):
        date = datetime(2023, 3, 15, 14, 30, 0)
        make_commit(self.tmpdir, date, "Backdated commit")
        code, stdout, _ = run_command(
            ["git", "log", "-1", "--format=%ai"],
            cwd=self.tmpdir
        )
        self.assertEqual(code, 0)
        self.assertIn("2023-03-15", stdout)

    def test_multiple_commits(self):
        dates = [
            datetime(2024, 1, 1, 9, 0, 0),
            datetime(2024, 1, 2, 10, 0, 0),
            datetime(2024, 1, 3, 11, 0, 0),
        ]
        for d in dates:
            make_commit(self.tmpdir, d)

        code, stdout, _ = run_command(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=self.tmpdir
        )
        # +1 for the initial commit from init_git_repo
        self.assertEqual(stdout, str(len(dates) + 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
