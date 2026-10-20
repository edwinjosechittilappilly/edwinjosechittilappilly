#!/usr/bin/env python3
"""Refresh the profile's selected public contribution counts and local SVG cards."""
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "profile"
ACCOUNT = "edwinjosechittilappilly"
PROJECTS = (
    ("Langflow", "langflow-ai/langflow", "Contributor"),
    ("OpenRAG", "langflow-ai/openrag", "Core contributor"),
    ("Quoptuna", "Qentora/quoptuna", "Founder & researcher"),
)
THEMES = {
    "dark": {"bg": "#0c1015", "panel": "#151b23", "text": "#f1f5f9", "muted": "#b1bdcd", "accent": "#8de4c3", "line": "#344150"},
    "light": {"bg": "#f4f7fa", "panel": "#ffffff", "text": "#14202b", "muted": "#506073", "accent": "#0b6b55", "line": "#c5ced8"},
}
START = "<!-- public-contributions:start -->"
END = "<!-- public-contributions:end -->"


def public_count(repository):
    query = f"repo:{repository} author:{ACCOUNT} is:pr is:merged is:public"
    api_url = "https://api.github.com/search/issues?" + urlencode({"q": query, "per_page": 1})
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "edwin-jose-public-profile",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(api_url, headers=headers), timeout=30) as response:
        result = json.load(response)
    count = result.get("total_count")
    if result.get("incomplete_results") is not False or type(count) is not int or count < 0:
        raise ValueError(f"Incomplete or invalid GitHub search results for {repository}; existing assets are not replaced.")
    return {"repository": repository, "merged_pull_requests": count, "api_url": api_url,
            "search_url": "https://github.com/search?" + urlencode({"q": query, "type": "pullrequests"})}


def svg_document(width, height, title, description, content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">'
            f'<title id="title">{escape(title)}</title><desc id="description">{escape(description)}</desc>'
            '<g font-family="Arial, Helvetica, sans-serif">' + content + '</g></svg>\n')


def header_svg(theme):
    c = THEMES[theme]
    return svg_document(840, 210, "Edwin Jose, PhD", "AI product and solution architecture. Open-source engineering. Quantum machine learning.",
        f'<rect x="1" y="1" width="838" height="208" rx="18" fill="{c["bg"]}" stroke="{c["line"]}"/>'
        f'<text x="36" y="89" fill="{c["text"]}" font-size="58" font-weight="700">Edwin Jose<tspan font-size="30" font-weight="400">, PhD</tspan></text>'
        f'<text x="38" y="137" fill="{c["accent"]}" font-size="25" font-weight="600">AI product &amp; solution architecture</text>'
        f'<text x="38" y="175" fill="{c["muted"]}" font-size="19">Open-source engineering · Quantum machine learning</text>')


def card_svg(project, theme):
    c = THEMES[theme]
    name = escape(project["name"])
    count = project["merged_pull_requests"]
    return svg_document(300, 190, f'{project["name"]}: {count} merged public pull requests',
        f'Merged pull requests authored by {ACCOUNT} in {project["repository"]}. Role: {project["role"]}.',
        f'<rect x="1" y="1" width="298" height="188" rx="16" fill="{c["panel"]}" stroke="{c["line"]}"/>'
        f'<text x="24" y="39" fill="{c["text"]}" font-size="23" font-weight="700">{name}</text>'
        f'<text x="24" y="65" fill="{c["muted"]}" font-size="14">{escape(project["role"])}</text>'
        f'<text x="22" y="132" fill="{c["accent"]}" font-size="57" font-weight="700">{count:,}</text>'
        f'<text x="24" y="163" fill="{c["muted"]}" font-size="16">Merged public pull requests</text>')


def contribution_markdown(projects, updated):
    parts = [f"Merged pull requests in selected public projects. Updated {updated[:10]} UTC.", ""]
    for project in projects:
        slug = project["name"].lower()
        alt = escape(f'{project["name"]}: {project["merged_pull_requests"]:,} merged public pull requests by {ACCOUNT}', quote=True)
        parts.append(
            f'<a href="{escape(project["search_url"], quote=True)}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/profile/{slug}-dark.svg">'
            f'<img src="assets/profile/{slug}-light.svg" width="260" height="165" alt="{alt}">'
            '</picture></a>')
    return "\n".join(parts)


def main():
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one public-contributions marker pair.")
    before, tail = readme.split(START)
    _, after = tail.split(END)
    projects = []
    for name, repository, role in PROJECTS:
        projects.append({"name": name, "role": role, **public_count(repository)})
    updated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    updated_readme = before + START + "\n" + contribution_markdown(projects, updated) + "\n" + END + after
    outputs = {"activity.json": json.dumps({"account": ACCOUNT, "updated_at": updated,
        "scope": "Merged pull requests authored by this account in the listed public repositories only.",
        "projects": projects}, indent=2) + "\n"}
    for theme in THEMES:
        outputs[f"header-{theme}.svg"] = header_svg(theme)
        for project in projects:
            outputs[f'{project["name"].lower()}-{theme}.svg'] = card_svg(project, theme)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for filename, content in outputs.items():
        (ASSETS / filename).write_text(content, encoding="utf-8")
    readme_path.write_text(updated_readme, encoding="utf-8")
    for project in projects:
        print(f'{project["name"]}: {project["merged_pull_requests"]} merged public pull requests')
    print(f"Updated {len(outputs)} local profile assets at {updated}.")


if __name__ == "__main__":
    main()
