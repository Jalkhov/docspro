import json
import os
import urllib.request

import requests
from tqdm import tqdm
import polib

good_headers = """\
msgid ""
msgstr ""
"Project-Id-Version: Flask 2.0.x\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2021-05-27 07:20-0400\n"
"PO-Revision-Date: 2022-02-15 21:58-0400\n"
"Language-Team: es_LA <pedrotorcattsoto@gmail.com>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel 2.9.1\n"
"Last-Translator: Pedro Torcatt <pedrotorcattsoto@gmail.com>\n"
"Language: es\n"
"X-Generator: Poedit 3.0\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"""

good_metadata = {'Content-Transfer-Encoding': '8bit',
                 'Content-Type': 'text/plain; charset=UTF-8',
                 'Generated-By': 'Babel 2.9.1',
                 'Language': 'xd',
                 'Language-Team': 'es_LA <pedrotorcattsoto@gmail.com>',
                 'Last-Translator': 'Pedro Torcatt <pedrotorcattsoto@gmail.com>',
                 'MIME-Version': '1.0',
                 'PO-Revision-Date': '2022-02-15 21:58-0400',
                 'POT-Creation-Date': '2021-05-27 07:20-0400',
                 'Plural-Forms': 'nplurals=2; plural=(n != 1);',
                 'Project-Id-Version': 'Flask 2.0.x',
                 'Report-Msgid-Bugs-To': '',
                 'X-Generator': 'Poedit 3.0'}

class repo_info:
    repo = None
    target_dir = None
    branch = None


class api_urls:
    recursive = "https://api.github.com/repos/{}/git/trees/{}?recursive=1"
    no_recursive = "https://api.github.com/repos/{}/git/trees/{}"


class OctodirException(Exception):
    pass


def fix_headers(pofile):
    """
    This fix .po headers for work with
    alexkiro/i18n-coverage action
    """
    file = polib.pofile(pofile)
    file.metadata['Language'] = good_metadata
    file.save(pofile)

def mkdirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)


class Octodir(object):

    def __init__(self):
        super(Octodir, self).__init__()
        self.folder_url = None
        self.output_folder = None

        self.repo = None
        self.target_dir = None
        self.branch = None

    def __get_raw_url(self, file_path, url):
        tmp_url = url.replace(
            'https://api.github.com/repos/',
            'https://raw.githubusercontent.com/')
        tmp_url = tmp_url.split('/git/blobs/')[0]
        tmp_url = tmp_url + '/' + self.branch + '/' + file_path

        return tmp_url

    def __get_repo_tree(self):
        api = requests.get(
            api_urls.recursive.format(self.repo, self.branch)).text
        files = json.loads(api)

        output = []
        location = dict()
        for (k, i) in enumerate(files['tree']):
            # If the target dir is in file path, that file
            # is inside target folder
            if self.target_dir in i['path']:
                if i['type'] == 'blob':
                    tmp = [i['path']]
                    tmp += [self.__get_raw_url(tmp[0], i['url'])]
                    output.append(tmp)
                else:
                    location[i['path']] = k
        files = output
        location = location

        return (files, location)

    def __scrutinize_url(self, folder_url):
        try:
            cutted_url = folder_url.replace('https://github.com/', '')
            splitted_url = cutted_url.split('/')

            owner = splitted_url[0]
            repo = splitted_url[1]
            branch = splitted_url[3]

            target_dir = [item for item in splitted_url[4:]]

            repo_data = repo_info()
            repo_data.repo = owner + '/' + repo
            repo_data.branch = branch
            repo_data.target_dir = "/".join(target_dir)

            return repo_data
        except IndexError:
            raise IndexError('Invalid repo url')

    def __api_response(self):
        repo_data = self.__scrutinize_url(self.folder_url)
        api = requests.get(api_urls.no_recursive.format(
            repo_data.repo, repo_data.branch)).text
        response = json.loads(api)

        return response

    def __check_valid_output(self):
        if os.path.isdir(self.output_folder):
            return True
        else:
            raise OctodirException('Invalid output directory')

    def __download(self, target_folder='*', recursive=True):
        data = self.__get_repo_tree()
        files = data[0]
        location = data[1]

        # mkdirs(".")

        if target_folder == '*':
            start = 0
        else:
            tmp_target = target_folder.replace('./', '')
            tmp_target = tmp_target.replace('../', '')

            # Remove "/"
            tmp_target = (tmp_target if tmp_target[-1] != '/'
                          else tmp_target[:-1])
            start = location[target_folder]

        with tqdm(total=len(files), desc="Downloading folder...") as pbar:
            for i in files[start:]:

                ndir = i[0].replace(
                    self.target_dir, self.target_dir.split('/')[-1:][0])
                if recursive or ndir.split(target_folder)[1].count('/') \
                        <= 1:

                    # Check output dir variable
                    mkdirs(os.path.join(self.output_folder, os.path.dirname(ndir)))

                    urllib.request.urlretrieve(
                        i[1], os.path.join(self.output_folder, ndir))

                    pofile = os.path.join(self.output_folder, ndir)
                    fix_headers(pofile)

                pbar.update(1)

    def dowload_folder(self, folder_url, output_folder):
        self.folder_url = folder_url
        self.output_folder = output_folder
        check_repo = self.__api_response()
        if 'message' in check_repo:
            raise OctodirException(check_repo['message'])
        else:
            if self.__check_valid_output() is True:
                scrutinized_url = self.__scrutinize_url(self.folder_url)
                self.repo = scrutinized_url.repo
                self.target_dir = scrutinized_url.target_dir
                self.branch = scrutinized_url.branch
                self.__download()
