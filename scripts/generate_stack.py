import os
import requests
from collections import defaultdict

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {"Authorization": f"token {TOKEN}"}

def get_repositories():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos

def get_languages(repo_name):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def aggregate_languages():
    language_totals = defaultdict(int)
    repos = get_repositories()

    for repo in repos:
        if repo["fork"]:
            continue

        languages = get_languages(repo["name"])
        for lang, bytes_count in languages.items():
            language_totals[lang] += bytes_count

    return language_totals

def update_readme(language_totals):
    sorted_langs = sorted(language_totals.items(), key=lambda x: x[1], reverse=True)

    tech_section = "## ⚡ Auto-Generated Tech Stack\n\n"
    for lang, _ in sorted_langs:
        tech_section += f"- {lang}\n"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!--TECH_STACK_START-->"
    end = "<!--TECH_STACK_END-->"

    new_content = (
        content.split(start)[0]
        + start + "\n\n"
        + tech_section
        + "\n"
        + end
        + content.split(end)[1]
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    langs = aggregate_languages()
    update_readme(langs)
