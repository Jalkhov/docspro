import json
import os
from pathlib import Path
from pprint import pprint

import polib
import requests
from octodir import Octodir
from prettytable import MARKDOWN, PrettyTable

base_repo_url = 'https://github.com/flaskcwg/flask-docs-{repo_code}/tree/main/docs/locales/{locl_code}'
badge_url = 'https://shields.io/badge/translated-{percent}%25-blue'
img_badge_prev = '![Progress](https://jalkhov.github.io/docspro/badge/{img})'
img_badge_code = f'`{img_badge_prev}`'
verbose = True

# This var saves the code in reponame and
# the code in locale directory
translation_repos = {'es': 'es', 'fr': 'fr', 'fa': 'fa', 'zh': 'zh_CN'}
# print(translation_repos[0])


def echo(msg):
    if verbose:
        print(msg)


def ensure_dirs():
    """
    Create all necesary folders
    """
    os.makedirs('for_deploy/data', exist_ok=True)  # folder for jsons
    os.makedirs('for_deploy/badge', exist_ok=True)  # folder for badges
    os.makedirs('docs', exist_ok=True)  # folder for translation repos


def generate_badge(lang, percent):
    """
    Generate and download the badges in for_deploy/badge folder
    """
    svg_data = requests.get(badge_url.format(percent=percent)).text
    with open(f'for_deploy/badge/{lang}_progress.svg', 'w') as file:
        file.write(svg_data)


def generate_jsons(lang, percent):
    """
    Generate json files with lang info
    trans_percent: Translation percentage from repo
    TODO: last-sync: Last sync with Flask repo
    """
    json_string = json.dumps({'trans_percent': percent})
    with open(f'for_deploy/data/{lang}_data.json', 'w') as outfile:
        outfile.write(json_string)


def get_badges():
    """
    Get downloaded badges
    """
    return os.listdir("for_deploy/badge")


def gen_badges_table():
    """
    Generate table with badges previews
    and embed codes
    """
    table = PrettyTable()
    table.set_style(MARKDOWN)
    table.field_names = ["Lang", "Preview", "Code"]
    table.align["Preview"] = "l"

    badges = get_badges()
    for badge in badges:
        lang = badge.split('_')[0]
        table.add_row([lang,
                       img_badge_prev.format(img=badge),
                       img_badge_code.format(img=badge)])

    return table


def generate_main_files():
    """
    Generate README.md and index.html
    """
    table = gen_badges_table()

    with open('.github/README_TEMPLATE.md', 'r') as readme_template:
        template_content = readme_template.read()

        with open('README.md', 'w') as readme_md:
            readme_content = template_content.format(table=table)
            readme_md.write(readme_content)

    with open('for_deploy/index.html', 'w') as outfile:
        outfile.write("<p>This site os only a mirror for host badges, please go to <a href='https://github.com/Jalkhov/docspro'>REPO</a> for full  info.</p>")


def get_trans_repos():
    """
    FROM NOW, ITS BETTER JUST SET TRANSLATION
    REPOS MANUALLY

    Get all translation repos from flaskcwg
    return just a list with lang codes
    """
    """
    flaskcwg_repos = 'https://api.github.com/orgs/flaskcwg/repos?type=all&per_page=15&page=1'
    trans_repos = requests.get(flaskcwg_repos).json()
    lang_codes = []

    for x in trans_repos:
        html_url = x['html_url']
        if 'flask-docs' in html_url:
            lang_codes.append(html_url)

    return lang_codes
    """
    pass


def calculate_translation(pofiles):
    """
    Calculate translate percentage of repo based in .po files
    """
    left = 0
    right = 0
    for popath in pofiles:
        pofile = polib.pofile(popath)

        total_strings = [e for e in pofile if not e.obsolete]
        percent_translated = pofile.percent_translated()

        left += len(total_strings) * percent_translated
        right += len(total_strings)

    return round(left / right, 2)


def main():
    ensure_dirs()
    langs = translation_repos

    # DOWNLOAD TRANSLATION REPOS LOCALE/<LANG> FOLDER
    for lang in langs:
        repo_code = lang
        locl_code = langs[lang]

        url = base_repo_url.format(repo_code=repo_code, locl_code=locl_code)
        echo(f'\n> Fetching: {url}')
        Octo = Octodir(url, 'docs')
        Octo.dowload_folder()

    # CALCULATE TRANSLATION PERCENTAGE
    for lang in langs:
        repo_code = lang
        local_code = langs[lang]

        echo("> Working in [" + local_code.upper() + "] lang")
        echo("\tCalculating translation percentage")

        lang_files = []
        for root, dirs, files in os.walk(f'docs/{local_code}'):
            for file in files:
                if file.endswith(".po"):
                    file_path = os.path.join(root, file)
                    lang_files.append(Path(file_path))

        percent = calculate_translation(lang_files)

        if int(percent) == 100:
            percent = 100

        echo(f'\tTranslation percentage: {percent}')

        # GENERATE AND DOWNLOAD THE BADGES
        echo("\tGenerating and downloading badge")
        generate_badge(repo_code, percent)

        # GENERATE JSON FILES
        echo("\tGenerating json file")
        generate_jsons(repo_code, percent)

    # GENERATE README.md AND index.html
    echo("> Generating README.md and index.html")
    generate_main_files()


if __name__ == '__main__':
    main()
