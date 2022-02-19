from octodir import Octodir
import os, sys
import json
import requests

repos = [['es', 'es'], ['fr', 'fr'], ['zh', 'zh_CN'], ['fa', 'fa']] # temporal, walk org repos
target = 'https://github.com/flaskcwg/flask-docs-{lang}/tree/main/docs/locales/{dial}'
folder = 'for_deploy/docs' # Current working directory
badge_url = 'https://shields.io/badge/translated-{cov}%25-green'

def download_docs():
	Octo = Octodir()
	os.makedirs('data', exist_ok=True) # Create folder for jsons and badges
	os.makedirs(folder, exist_ok=True)
	for lang in repos:
		lng = lang[0]
		dlc = lang[1]

		Octo.dowload_folder(target.format(lang=lng, dial=dlc), folder)

def generate_jsons(lang, cov):
	cov = "%.2f" % (float(cov))
	json_string = json.dumps({'cov':cov})
	with open(f'data/{lang}_cov.json', 'w') as outfile:
	    outfile.write(json_string)

def generate_badge(lang, cov):
	svg_data = requests.get(badge_url.format(cov)).text
    with open(f'data/{lang}_progress.svg', 'w') as file:
        file.write(svg_data)


def main(args):
	if len(args) > 1 and args[1] == "--download":
		download_docs()
	else:
		lang = args[1].split('--')[1]
		cov = args[2]
		generate_jsons(lang, cov)
		generate_badge(lang, cov)

if __name__ == '__main__':
	main(sys.argv)