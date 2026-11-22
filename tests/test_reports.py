import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from clientops.reports import render_weekly_report

class ReportTests(unittest.TestCase):
    def test_report_uses_git_commit_subjects(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d); subprocess.run(["git","init","-q",str(repo)],check=True)
            (repo/"README.md").write_text("starter")
            env=os.environ.copy()
            env.update({"GIT_AUTHOR_NAME":"Test Contributor","GIT_AUTHOR_EMAIL":"test@example.com","GIT_COMMITTER_NAME":"Test Contributor","GIT_COMMITTER_EMAIL":"test@example.com","GIT_AUTHOR_DATE":"2026-11-20T12:00:00","GIT_COMMITTER_DATE":"2026-11-20T12:00:00"})
            subprocess.run(["git","-C",str(repo),"add","README.md"],check=True,env=env)
            subprocess.run(["git","-C",str(repo),"commit","-q","-m","feat: add starter README"],check=True,env=env)
            report=render_weekly_report(repo,"2026-11-19","2026-11-21")
        self.assertIn("Weekly progress report",report)
        self.assertIn("feat: add starter README",report)

if __name__=="__main__": unittest.main()
