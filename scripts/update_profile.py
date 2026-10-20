#!/usr/bin/env python3
"""Build a responsive professional profile from verified biography and public GitHub data."""
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import textwrap
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "profile"
ACCOUNT = "edwinjosechittilappilly"
PROJECTS = (
    ("Langflow", "langflow-ai/langflow", "Contributor", "Agent systems, MCP integrations, backend components and testing."),
    ("OpenRAG", "langflow-ai/openrag", "Core contributor", "Retrieval and orchestration, configuration, reproducible environments and developer documentation."),
    ("Quoptuna", "Qentora/quoptuna", "Founder & first-author researcher", "Explainable quantum machine learning, optimization, backend and interface development."),
)
PUBLICATIONS = (
    {"title": "Quoptuna: Automated Optimization and Governance for Quantum Machine Learning", "year": 2026,
     "venue": "IEEE Systems, Man, and Cybernetics Magazine", "url": "https://doi.org/10.1109/MSMC.2025.3613072"},
    {"title": "Quoptuna: An Open-Source Framework for Explainable Quantum Machine Learning", "year": 2025,
     "venue": "IEEE INTCEC", "url": "https://doi.org/10.1109/INTCEC65580.2025.11256089"},
    {"title": "Design and Development of an Open-Source Toolkit for Quantum Machine Learning", "year": 2025,
     "venue": "IEEE RASSE", "url": "https://doi.org/10.1109/RASSE64831.2025.11315342"},
)
THEMES = {
    "dark": {"bg": "#0c1015", "panel": "#151b23", "text": "#f1f5f9", "muted": "#b1bdcd", "accent": "#8de4c3", "line": "#344150"},
    "light": {"bg": "#f4f7fa", "panel": "#ffffff", "text": "#14202b", "muted": "#506073", "accent": "#0b6b55", "line": "#c5ced8"},
}
START = "<!-- profile-overview:start -->"
END = "<!-- profile-overview:end -->"


def public_count(repository):
    query = f"repo:{repository} author:{ACCOUNT} is:pr is:merged is:public"
    api_url = "https://api.github.com/search/issues?" + urlencode({"q": query, "per_page": 1})
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "edwin-jose-public-profile",
               "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(api_url, headers=headers), timeout=30) as response:
        result = json.load(response)
    count = result.get("total_count")
    if result.get("incomplete_results") is not False or type(count) is not int or count < 0:
        raise ValueError(f"Incomplete or invalid GitHub results for {repository}; existing profile is not replaced.")
    return {"repository": repository, "merged_pull_requests": count, "api_url": api_url,
            "search_url": "https://github.com/search?" + urlencode({"q": query, "type": "pullrequests"})}


def text(x, y, value, color, size=17, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{escape(str(value))}</text>')


def paragraph(x, y, value, width, color, size=17, weight=400, leading=25):
    # Conservative line lengths keep the Arial/Helvetica fallback readable on GitHub.
    lines = textwrap.wrap(value, width=max(12, int(width / (size * .55))), break_long_words=False)
    return "".join(text(x, y + i * leading, line, color, size, weight) for i, line in enumerate(lines)), y + len(lines) * leading


def panel(x, y, width, height, content, colors):
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16" '
            f'fill="{colors["panel"]}" stroke="{colors["line"]}"/>' + content)


def engineering(x, y, width, projects, colors):
    content = text(x + 24, y + 37, "Engineering in the open", colors["text"], 22, 700)
    content += text(x + 24, y + 65, "Merged PRs in selected public projects", colors["muted"], 15)
    cursor = y + 107
    for i, project in enumerate(projects):
        content += text(x + 24, cursor, project["name"], colors["text"], 22, 700)
        content += text(x + width - 24, cursor + 2, f'{project["merged_pull_requests"]:,}', colors["accent"], 31, 700, "end")
        role, cursor = paragraph(x + 24, cursor + 29, project["role"], width - 48, colors["accent"], 15, 500, 22)
        content += role
        prose, cursor = paragraph(x + 24, cursor + 6, project["description"], width - 48, colors["muted"], 16, leading=24)
        content += prose
        if i < len(projects) - 1:
            content += f'<path d="M{x + 24} {cursor + 12}H{x + width - 24}" stroke="{colors["line"]}"/>'
        cursor += 47
    height = cursor - y - 6
    return panel(x, y, width, height, content, colors), y + height


def research(x, y, width, colors):
    content = text(x + 24, y + 37, "Selected publications", colors["text"], 22, 700)
    content += text(x + 24, y + 65, "Quantum ML, optimization and AI education", colors["muted"], 15)
    cursor = y + 108
    for i, paper in enumerate(PUBLICATIONS):
        content += text(x + 24, cursor, paper["year"], colors["accent"], 16, 700)
        title, cursor = paragraph(x + 24, cursor + 29, paper["title"], width - 48, colors["text"], 17, 600, 25)
        content += title
        venue, cursor = paragraph(x + 24, cursor + 8, paper["venue"], width - 48, colors["muted"], 15, leading=22)
        content += venue
        if i < len(PUBLICATIONS) - 1:
            content += f'<path d="M{x + 24} {cursor + 12}H{x + width - 24}" stroke="{colors["line"]}"/>'
        cursor += 44
    height = cursor - y - 3
    return panel(x, y, width, height, content, colors), y + height


def approach(x, y, width, colors):
    content = text(x + 24, y + 37, "Architecture in practice", colors["text"], 22, 700)
    cursor = y + 79
    for label, detail in (
        ("Make the system clear", "Define component responsibilities, interfaces and important trade-offs."),
        ("Test the uncertain parts", "Use focused proofs of concept and evaluation to guide implementation."),
        ("Help teams move forward", "Share technical context, mentor contributors and make handoffs understandable."),
    ):
        content += text(x + 24, cursor, label, colors["accent"], 16, 700)
        prose, cursor = paragraph(x + 24, cursor + 26, detail, width - 48, colors["muted"], 16, leading=24)
        content += prose
        cursor += 22
    height = cursor - y + 1
    return panel(x, y, width, height, content, colors), y + height


def recognition(x, y, width, colors):
    content = text(x + 24, y + 37, "Recognition & foundation", colors["text"], 22, 700)
    cursor = y + 80
    for label, detail in (
        ("IBM Outstanding Technical Achievement Award", "2026"),
        ("IBM TCAP Leader Award", "Technical Collaboration Achievement Program, 2026"),
        ("IBM Open Source Strategic Committer", "Open-source stewardship and contribution"),
        ("Research foundation", "Computer Science PhD, specializing in Quantum Machine Learning."),
    ):
        label_svg, cursor = paragraph(x + 24, cursor, label, width - 48, colors["text"], 16, 600, 24)
        content += label_svg
        detail_svg, cursor = paragraph(x + 24, cursor + 3, detail, width - 48, colors["muted"], 15, leading=22)
        content += detail_svg
        cursor += 22
    height = cursor - y + 2
    return panel(x, y, width, height, content, colors), y + height


def toolkit(x, y, width, colors, mobile):
    content = text(x + 24, y + 37, "A toolkit shaped by the problem", colors["text"], 22, 700)
    groups = (
        ("AI workflows", "Python, Langflow, LangChain, MCP, Hugging Face, Transformers"),
        ("Services & deployment", "FastAPI, Flask, Docker, AWS, MongoDB"),
        ("Experiments & optimization", "scikit-learn, TensorFlow, Keras, Optuna, Hyperopt, Matplotlib"),
        ("Quantum learning", "PennyLane, Qiskit, quantum machine learning"),
    )
    columns = 1 if mobile else 2
    group_width = (width - 48 - 24 * (columns - 1)) / columns
    cursors = [y + 82] * columns
    for i, (label, detail) in enumerate(groups):
        column = i % columns
        left = x + 24 + column * (group_width + 24)
        content += text(left, cursors[column], label, colors["accent"], 16, 700)
        detail_svg, cursor = paragraph(left, cursors[column] + 27, detail, group_width, colors["muted"], 16, leading=24)
        content += detail_svg
        cursors[column] = cursor + 25
    height = max(cursors) - y + 1
    return panel(x, y, width, height, content, colors), y + height


def profile_svg(projects, updated, theme, mobile):
    colors = THEMES[theme]
    width = 420 if mobile else 960
    margin = 20 if mobile else 32
    inner = width - 2 * margin
    content = text(margin, 73 if mobile else 91, "Edwin Jose, PhD", colors["text"], 42 if mobile else 60, 700)
    cursor = 118 if mobile else 139
    for value, size, color in (
        ("AI product & solution architecture", 23 if mobile else 27, colors["accent"]),
        ("Software Engineer at IBM", 17 if mobile else 19, colors["text"]),
        ("Computer Science PhD · Western Michigan University", 16 if mobile else 18, colors["muted"]),
    ):
        line, cursor = paragraph(margin, cursor, value, inner, color, size, 500, 29 if mobile else 30)
        content += line
        cursor += 9
    bio, cursor = paragraph(margin, cursor + 8, "I connect research, system design and hands-on engineering to turn AI ideas into useful software.", inner, colors["muted"], 17, leading=26)
    content += bio
    cursor += 32
    if mobile:
        for render in (lambda x, y, w, c: engineering(x, y, w, projects, c), research, approach, recognition):
            section, cursor = render(margin, cursor, inner, colors)
            content += section
            cursor += 20
    else:
        column_width = (inner - 24) / 2
        left, left_bottom = engineering(margin, cursor, column_width, projects, colors)
        right, right_bottom = research(margin + column_width + 24, cursor, column_width, colors)
        content += left + right
        left, left_bottom = approach(margin, left_bottom + 24, column_width, colors)
        right, right_bottom = recognition(margin + column_width + 24, right_bottom + 24, column_width, colors)
        content += left + right
        cursor = max(left_bottom, right_bottom) + 24
    tools, cursor = toolkit(margin, cursor, inner, colors, mobile)
    content += tools
    footer, end = paragraph(margin, cursor + 30, f'Public GitHub contribution data refreshed {updated[:10]} UTC.', inner, colors["muted"], 13, leading=20)
    content += footer
    height = int(end + 20)
    description = ("Edwin Jose, Software Engineer at IBM and Computer Science PhD. Selected public contribution counts: "
        + "; ".join(f'{p["name"]}: {p["merged_pull_requests"]} merged pull requests' for p in projects)
        + ". Selected peer-reviewed publications, architecture practice, recognition and technical toolkit. Full accessible details and paper links are available on the linked portfolio.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">'
        f'<title id="title">Edwin Jose, PhD: engineering and research profile</title><desc id="description">{escape(description)}</desc>'
        f'<rect width="{width}" height="{height}" rx="18" fill="{colors["bg"]}"/>'
        '<g font-family="Arial, Helvetica, sans-serif">' + content + '</g></svg>\n')


def profile_markdown(projects):
    alt = escape("Edwin Jose, PhD. Software Engineer at IBM focused on AI product and solution architecture. "
        + "; ".join(f'{p["name"]}: {p["merged_pull_requests"]:,} merged public pull requests' for p in projects)
        + ". Selected publications, architecture practice, recognition and toolkit. Use the links below for the accessible portfolio and individual papers.", quote=True)
    return ('<picture>\n'
        '  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/profile/profile-mobile-dark.svg">\n'
        '  <source media="(max-width: 600px)" srcset="assets/profile/profile-mobile-light.svg">\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/profile/profile-desktop-dark.svg">\n'
        f'  <img src="assets/profile/profile-desktop-light.svg" width="960" alt="{alt}">\n'
        '</picture>')


def main():
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one profile-overview marker pair.")
    before, tail = readme.split(START)
    _, after = tail.split(END)
    projects = [{"name": name, "role": role, "description": detail, **public_count(repository)}
                for name, repository, role, detail in PROJECTS]
    updated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    updated_readme = before + START + "\n" + profile_markdown(projects) + "\n" + END + after
    outputs = {"activity.json": json.dumps({"account": ACCOUNT, "updated_at": updated,
        "scope": "Merged pull requests authored by this account in the listed public repositories only.",
        "projects": projects, "selected_publications": PUBLICATIONS}, indent=2) + "\n"}
    for theme in THEMES:
        for mobile in (False, True):
            size = "mobile" if mobile else "desktop"
            outputs[f"profile-{size}-{theme}.svg"] = profile_svg(projects, updated, theme, mobile)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for filename, content in outputs.items():
        (ASSETS / filename).write_text(content, encoding="utf-8")
    readme_path.write_text(updated_readme, encoding="utf-8")
    for project in projects:
        print(f'{project["name"]}: {project["merged_pull_requests"]} merged public pull requests')
    print(f"Updated responsive SVG profile at {updated}.")


if __name__ == "__main__":
    main()
