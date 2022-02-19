from octodir import Octodir
import os

repos = ['es', 'fr', 'zh', 'fa'] # temporal, walk org repos
Octo = Octodir()

target = 'https://github.com/flaskcwg/flask-docs-{lang}/tree/main/docs/locales/{lang}'
folder = 'for_deploy/docs' # Current working directory

os.makedirs(folder, exist_ok=True)
for lang in repos:
	print("> Downloading: ", lang.upper())
	Octo.dowload_folder(target.format(lang=lang), folder)