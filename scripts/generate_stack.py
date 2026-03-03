import os
import requests
from collections import defaultdict

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {"Authorization": f"token {TOKEN}"}

BADGE_MAP = {
    "Python": ("Python", "3776AB", "python"),
    "JavaScript": ("JavaScript", "F7DF1E", "javascript"),
    "TypeScript": ("TypeScript", "3178C6", "typescript"),
    "Java": ("Java", "ED8B00", "java"),
    "C++": ("C++", "00599C", "cplusplus"),
    "HTML": ("HTML5", "E34F26", "html5"),
    "CSS": ("CSS3", "1572B6", "css3"),
    "Jupyter Notebook": ("Jupyter", "F37626", "jupyter"),
    "Shell": ("Shell", "121011", "gnu-bash"),
}

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

def generate_badges(language_totals):
    sorted_langs = sorted(language_totals.items(), key=lambda x: x[1], reverse=True)

    badges = ""
    for lang, _ in sorted_langs:
        if lang in BADGE_MAP:
            label, color, logo = BADGE_MAP[lang]
            badges += f"![{label}](https://img.shields.io/badge/{label}-{color}?style=for-the-badge&logo={logo}&logoColor=white)\n"
        else:
            badges += f"![{lang}](https://img.shields.io/badge/{lang}-blue?style=for-the-badge)\n"

    return badges

def update_readme(badges):
    start = "<!--TECH_STACK_START-->"
    end = "<!--TECH_STACK_END-->"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new_content = (
        content.split(start)[0]
        + start + "\n\n"
        + badges
        + "\n"
        + end
        + content.split(end)[1]
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    langs = aggregate_languages()
    badges = generate_badges(langs)
    update_readme(badges)
