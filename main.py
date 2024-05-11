import json
import os
from pathlib import Path
import polib
import requests
from octodir import Octodir
from prettytable import MARKDOWN, PrettyTable
import importlib.metadata
import toml

API_KEY = os.environ['PERSONAL_API_KEY']

BASE_REPO_URL = 'https://github.com/flaskcwg/flask-docs-{repo_code}/tree/main'

BADGE_URL = ('https://img.shields.io/badge/Docs_{docs_version}-{percent}%25-blue'
             '?logo=read-the-docs&logoColor=white')

IMG_BADGE_PREV = '![Progress](https://jalkhov.github.io/docspro/badge/{img})'

IMG_BADGE_CODE = f'`{IMG_BADGE_PREV}`'

TRANSLATION_REPOS = {'es': 'es', 'fr': 'fr', 'fa': 'fa', 'zh': 'zh_CN'}

VERBOSE = True


def echo(msg):
    if VERBOSE:
        print(msg)


def ensure_dirs():
    os.makedirs('for_deploy/data', exist_ok=True)
    os.makedirs('for_deploy/badge', exist_ok=True)
    os.makedirs('repos', exist_ok=True)


def get_file_contents(file_path):
    with open(file_path, 'r') as f:
        return f.read()

"""
Changed the way to obtain lask version of base repository due to:

warnings.warn(
    "The '__version__' attribute is deprecated and will be removed in"
    " Flask 3.1. Use feature detection or"
    " 'importlib.metadata.version(\"flask\")' instead.",
    DeprecationWarning,
    stacklevel=2,
)

In __init__.py from flask source, some day will search a solution ;)
"""
def get_docs_version(lang_code):
    file_path = Path(f'repos/{lang_code}/pyproject.toml')
    # file_path = Path(f'pyproject.toml')
    try:
        # Lee el contenido del archivo pyproject.toml
        with open(file_path, 'r') as toml_file:
            toml_contents = toml.load(toml_file)
            # Busca la clave 'version' en la sección '[project]'
            version = toml_contents.get('project', {}).get('version', '')
    except FileNotFoundError:
        # Si no se encuentra el archivo, maneja la excepción apropiadamente
        version = 'No se encontró el archivo pyproject.toml'

    echo(version)
    return version


def generate_badge(lang, percent, docs_version):
    svg_data = requests.get(BADGE_URL.format(percent=percent, docs_version=docs_version)).text
    with open(f'for_deploy/badge/{lang}_progress.svg', 'w') as file:
        file.write(svg_data)


def generate_jsons(lang, percent, docs_version):
    data = {'trans_percent': percent, 'docs_version': docs_version}
    with open(f'for_deploy/data/{lang}_data.json', 'w') as outfile:
        json.dump(data, outfile)


def get_badges():
    return os.listdir('for_deploy/badge')


def generate_badge_preview(img):
    return IMG_BADGE_PREV.format(img=img)


def generate_badge_code(img):
    return IMG_BADGE_CODE.format(img=img)


def gen_badges_table():
    table = PrettyTable()
    table.set_style(MARKDOWN)
    table.field_names = ['Lang', 'Preview', 'Code']
    table.align['Preview'] = 'l'

    badges = get_badges()
    for badge in badges:
        lang = badge.split('_')[0]
        preview = generate_badge_preview(badge)
        code = generate_badge_code(badge)
        table.add_row([lang, preview, code])

    return table


def generate_main_files():
    table = gen_badges_table()

    with open('.github/README_TEMPLATE.md', 'r') as readme_template, open('README.md', 'w') as readme_md:
        template_content = readme_template.read()
        readme_content = template_content.format(table=table)
        readme_md.write(readme_content)

    with open('for_deploy/index.html', 'w') as outfile:
        outfile.write("<p>This site os only a mirror for host badges, please go to <a "
                      "href='https://github.com/Jalkhov/docspro'>REPO</a> for full  info.</p>")


def calculate_translation(pofiles):
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
    langs = TRANSLATION_REPOS

    for lang in langs:
        repo_code = lang
        local_code = langs[lang]
        
        echo(f'\t> Fetching: {BASE_REPO_URL.format(repo_code=repo_code, local_code=local_code)}')
        os.makedirs(f'repos/{local_code}', exist_ok=True)
        url = BASE_REPO_URL.format(repo_code=repo_code, local_code=local_code)
        octo = Octodir(url, f'repos/{local_code}', API_KEY)
        octo.dowload_folder()

        echo(f'\n# Processing {local_code.upper()} #')
        
        pofiles = []
        for root, dirs, files in os.walk(f'repos/{local_code}/docs/locales/{local_code}'):
            for file in files:
                if file.endswith(".po"):
                    file_path = os.path.join(root, file)
                    pofiles.append(Path(file_path))

        percent_translated = calculate_translation(pofiles)

        echo(f'\t> Generating badge for {local_code}')

        docs_version = get_docs_version(local_code)
        echo(f'\t> Docs version: {docs_version}')

        generate_badge(repo_code, percent_translated, docs_version)

        echo(f'\t> Generating JSON with data for {local_code}')
        generate_jsons(repo_code, percent_translated, docs_version)

    generate_main_files()


if __name__ == '__main__':
    main()
