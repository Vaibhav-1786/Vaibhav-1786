import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

USERNAME = "Vaibhav-1786"
README = Path("README.md")
MAX_PROJECTS = 6
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"


def github_get(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-readme-project-updater",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def clean(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def format_date(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except Exception:
        return "—"


def main():
    repos = []
    for page in range(1, 4):
        url = (
            f"https://api.github.com/users/{urllib.parse.quote(USERNAME)}/repos"
            f"?per_page=100&page={page}&sort=updated&direction=desc"
        )
        data = github_get(url)
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break

    selected = [
        r for r in repos
        if not r.get("fork")
        and not r.get("archived")
        and r.get("name") != USERNAME
    ][:MAX_PROJECTS]

    rows = []
    for repo in selected:
        name = clean(repo.get("name"))
        url = repo.get("html_url", f"https://github.com/{USERNAME}/{repo['name']}")
        description = clean(repo.get("description")) or "Open-source project and development work."
        updated = format_date(repo.get("updated_at", ""))
        rows.append(f"| [{name}]({url}) | {description} | {updated} |")

    if rows:
        body = "\n".join(rows)
    else:
        body = "| _No repositories found_ | Check the repository visibility and GitHub API access. | — |"

    generated = f"""{START}\n> Projects are updated automatically from my public GitHub repositories.\n\n| Project | Description | Updated |\n|---|---|---|\n{body}\n\n**[→ View all repositories](https://github.com/{USERNAME}?tab=repositories)**\n{END}"""

    text = README.read_text(encoding="utf-8")
    start = text.find(START)
    end = text.find(END)
    if start == -1 or end == -1 or end < start:
        raise SystemExit("Project markers not found in README.md")
    end += len(END)
    updated_readme = text[:start] + generated + text[end:]
    if updated_readme != text:
        README.write_text(updated_readme, encoding="utf-8")
        print("README.md project list updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
