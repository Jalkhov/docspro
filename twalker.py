import re

import requests

list_repos = 'https://api.github.com/users/flaskcwg/repos'
list_tree = 'https://api.github.com/repos/flaskcwg/{repo}/git/trees/main?recursive=1'
locale_pattern = r'docs\/locales\/[a-z]{2}_[A-Z]{2}$|docs\/locales\/[a-z]{2}$'

def clean(limiter, string):
    """
    limiter
    - For repo names
    / For locale path
    """
    return string.split(limiter)[2]

class TWalker(object):
    """
    Get translation repos from FlaskCWG with locale code
    """
    def __init__(self):
        super(TWalker, self).__init__()

    def translation_repos(self):
        """
        Walk repos from organization and
        get only translation repos
        """
        trans_repos = []
        req = requests.get(list_repos).json()
        for repo in req:
            repo_name = repo['name']
            if 'flask-docs' in repo_name:
                trans_repos.append(repo_name)

        return trans_repos

    def langs_data(self):
        """
        Due to locale variantes (like zh_CN) its
        necesary walk repos in search of this code
        and not assume who is the same of the lang code
        """
        trans_repos = self.translation_repos()
        data = []
        for repo in trans_repos:
            req = requests.get(list_tree.format(repo=repo)).json()
            repo_tree = req['tree']
            locale_dir = [x['path'] for x in repo_tree if re.search(locale_pattern, x['path']) != None][0]
            if locale_dir:
                data.append([clean('-', repo), clean('/', locale_dir)])
                continue

        return data
