from octodir import Octodir
import os, sys
import json

repos = [['es', 'es'], ['fr', 'fr'], ['zh', 'zh_CN'], ['fa', 'fa']] # temporal, walk org repos
target = 'https://github.com/flaskcwg/flask-docs-{lang}/tree/main/docs/locales/{dial}'
folder = 'for_deploy/docs' # Current working directory

def download_docs():
	Octo = Octodir()

	os.makedirs(folder, exist_ok=True)
	for lang in repos:
		lng = lang[0]
		dlc = lang[1]

		Octo.dowload_folder(target.format(lang=lng, dial=dlc), folder)

def generate_jsons(lang, cov):
	json_string = json.dumps({'cov':cov})
	with open(f'for_deploy/{lang}_cov.json', 'w') as outfile:
	    outfile.write(json_string)

def main(args):
	if len(args) > 1 and args[1] == "--download":
		download_docs()
	elif:
		lang = args[1].split('--')[1]
		cov = args[2]
		generate_jsons(lang, cov)

if __name__ == '__main__':
	main(sys.argv)