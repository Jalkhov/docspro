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

def main():
	if sys.argv[1:]:
		print(sys.argv[0])
	else:
		download_docs()

if __name__ == '__main__':
	main()