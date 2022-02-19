from octodir import Octodir
import os, sys
import json

repos = ['es', 'fr', 'zh', 'fa'] # temporal, walk org repos
target = 'https://github.com/flaskcwg/flask-docs-{lang}/tree/main/docs/locales/{lang}'
folder = 'for_deploy/docs' # Current working directory

def download_docs():
	Octo = Octodir()

	os.makedirs(folder, exist_ok=True)
	for lang in repos:
		print("> Downloading: ", lang.upper())
		Octo.dowload_folder(target.format(lang=lang), folder)

def generate_jsons():
	pass

def main(args):
	if len(args) > 1 and args[1] == "--download":
		download_docs()
	elif len(args) > 1 and args[1] == "--jsons"::
		print(args)

if __name__ == '__main__':
	main(sys.argv)