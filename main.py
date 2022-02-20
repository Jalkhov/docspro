import json
import os
import sys

import requests
from dayman import today
from octodir import Octodir
from prettytable import MARKDOWN, PrettyTable

repos = [['es', 'es'], ['fr', 'fr'], ['zh', 'zh_CN'], ['fa', 'fa']] # temporal, walk org repos
repo_locales_url = 'https://github.com/flaskcwg/flask-docs-{lang}/tree/main/docs/locales/{dial}'
docs_dir = 'for_deploy/docs' # Folder for languages
badge_url = 'https://shields.io/badge/translated-{cov}%25-blue'
img_badge_prev = '![Progress](https://jalkhov.github.io/docspro/badge/{img})'
img_badge_code = f'`{img_badge_prev}`'


def round_cov(cov):
    """
    Format coverage to only
    two decimals
    """
    return "%.2f" % (float(cov))


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
    badges = get_badges()

    for badge in badges:
        lang = badge.split('_')[0]
        table.add_row([lang,
                       img_badge_prev.format(img=badge),
                       img_badge_code.format(img=badge)])
    return table


def download_docs():
    """
    Download language docs
    """
    Octo = Octodir()
    os.makedirs('for_deploy/data', exist_ok=True) # Create folder for jsons
    os.makedirs('for_deploy/badge', exist_ok=True) # Create folder for badges
    os.makedirs(docs_dir, exist_ok=True) # Create folde for languages
    for lang in repos:
        lng = lang[0]
        dlc = lang[1]

        Octo.dowload_folder(repo_locales_url.format(lang=lng, dial=dlc), docs_dir)


def generate_main_files():
    """
    Generate main README.md
    and index.html
    """
    table = gen_badges_table()
    print(table)
    with open('.github/README_TEMPLATE.md','r') as readme_template:
        template_content = readme_template.read()

        with open('README.md', 'w') as readme_md:
            readme_content = template_content.format(table=table, last_sync=today())
            readme_md.write(readme_content)

    with open(f'for_deploy/index.html', 'w') as outfile:
        outfile.write("<p>This site os only a mirror for host badges, please go to <a href='https://github.com/Jalkhov/docspro'>REPO</a> for full  info.</p>")


def generate_jsons(lang, cov):
    cov = round_cov(cov)
    json_string = json.dumps({'cov':cov})
    with open(f'for_deploy/data/{lang}_cov.json', 'w') as outfile:
        outfile.write(json_string)


def generate_badge(lang, cov):
    cov = round_cov(cov)
    svg_data = requests.get(badge_url.format(cov=cov)).text
    with open(f'for_deploy/badge/{lang}_progress.svg', 'w') as file:
        file.write(svg_data)


def main(args):
    if len(args) > 1:
        option = args[1]
        if option == "--download":
            download_docs()

        elif option == "--gen":
            #--gen fa ${{ steps.faCoverage.outputs.coverage }}
            lang = args[2]
            cov = args[3]
            generate_jsons(lang, cov)
            generate_badge(lang, cov)

        elif args[1] == "--build":
            generate_main_files()

if __name__ == '__main__':
    main(sys.argv)
