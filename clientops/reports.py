"""Generate a weekly activity report from Git commit subjects."""
import subprocess
from datetime import date,datetime,time
from pathlib import Path

def render_weekly_report(repo_path,since,until):
    start=date.fromisoformat(since); end=date.fromisoformat(until)
    if end<start: raise ValueError("--until must be on or after --since")
    repo=Path(repo_path).expanduser().resolve()
    if not repo.exists(): raise FileNotFoundError(f"Repository path does not exist: {repo}")
    pretty="%h%x1f%ad%x1f%an%x1f%s"
    cmd=["git","-C",str(repo),"log","--all",f"--since={datetime.combine(start,time.min).isoformat()}",f"--until={datetime.combine(end,time.max).isoformat()}","--date=short",f"--pretty=format:{pretty}"]
    try: result=subprocess.run(cmd,check=True,capture_output=True,text=True,encoding="utf-8")
    except FileNotFoundError as exc: raise RuntimeError("Git is not installed or unavailable on PATH") from exc
    lines=["# Weekly progress report","",f"**Repository:** {repo.name}  ",f"**Period:** {since} to {until}  ",f"**Generated:** {date.today().isoformat()}","","This report is based on Git commit subjects and does not verify task completion.",""]
    commits=[line.split("\x1f",3) for line in result.stdout.splitlines() if line]
    if not commits: lines += ["No commits were found in this date range.",""]
    else:
        lines += [f"**Commit count:** {len(commits)}","","## Commit log",""]
        lines += [f"- {d} — {subject} — {author} ({sha})" for sha,d,author,subject in commits]
        lines.append("")
    return "\n".join(lines)

def write_weekly_report(repo_path,since,until,output_path):
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(render_weekly_report(repo_path,since,until),encoding="utf-8"); return out
