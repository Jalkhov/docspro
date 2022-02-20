from octodir import Octodir
import os, sys
import json
import requests
from prettytable import PrettyTable, MARKDOWN

repos = [['es', 'es'], ['fr', 'fr'], ['zh', 'zh_CN'], ['fa', 'fa']] # temporal, walk org repos
target = 'https://github.com/flaskcwg/flask-docs-{lang}/tree/main/docs/locales/{dial}'
folder = 'for_deploy/docs' # Current working directory
badge_url = 'https://shields.io/badge/translated-{cov}%25-green'
img_badge_prev = '![Progress](https://jalkhov.github.io/docspro/badge/{img_url})'
img_badge_code = f'`{img_badge_prev}`'


def get_badges():
    return os.listdir("for_deploy/badge")

def gen_badges_table():
    table = PrettyTable()
    table.set_style(MARKDOWN)
    table.field_names = ["Preview", "Code"]
    badges = get_badges()

    for badge in badges:
        table.add_row([img_badge_prev.format(img_url=badge),
                       img_badge_code.format(img_url=badge)])
    return table

def download_docs():
    Octo = Octodir()
    os.makedirs('for_deploy/data', exist_ok=True) # Create folder for jsons
    os.makedirs('for_deploy/badge', exist_ok=True) # Create folder for badges
    os.makedirs(folder, exist_ok=True)
    for lang in repos:
        lng = lang[0]
        dlc = lang[1]

        Octo.dowload_folder(target.format(lang=lng, dial=dlc), folder)

def round_cov(cov):
    return "%.2f" % (float(cov))

def generate_index():
    table = gen_badges_table()
    with open('.github/README_TEMPLATE.md','r') as template:
        content = template.read()

        with open('README.md', 'w') as output:
            content = content.format(table=table)
            output.write(content)

    with open(f'for_deploy/index.html', 'w') as outfile:
        outfile.write("<h1>Docspro</h1>")



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
    if len(args) > 1 and args[1] == "--download":
        download_docs()
    else:
        lang = args[1].split('--')[1]
        cov = args[2]
        generate_jsons(lang, cov)
        generate_badge(lang, cov)
        generate_index()

if __name__ == '__main__':
    main(sys.argv)