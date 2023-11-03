from ablog.conf import *

org = "geometor"
org_name = "geometor"

repo = "model"
repo_name = "model"

blog_title = f'{org_name} • {repo_name}'
html_title = f'{org_name} • {repo_name}'
project = f'{org_name} • {repo_name}'
version = ''  # The short X.Y version.
release = ''  # The full version, including alpha/beta/rc tags.

copyright = f'{year}, {org_name}'
author = f'{org_name}'

# Base URL for the website, required for generating feeds.
# e.g. blog_baseurl = "http://example.com/"
blog_baseurl = f'https://{org}.github.io/{repo}'
html_base_url = blog_baseurl
html_baseurl = blog_baseurl

blog_authors = {
    "phi": ("phi ARCHITECT", None),
}

extensions.append('sphinx_rtd_theme')

html_theme = 'sphinx_rtd_theme'

html_css_files = [ "css/rtd-dark.css" ]

html_theme_options = {
    #  'logo': 'logo.png',
    #  'logo_name': True,
    #  'github_user': org,
    #  'github_repo': repo,
    #  'github_button': True,
    'navigation_depth': -1,
    'prev_next_buttons_location': 'both',
}
html_context = {
    "display_github": True, # Integrate GitHub
    "github_user": org, # Username
    "github_repo": repo, # Repo name
    "github_version": "main", # Version
    "conf_py_path": "/docsrc/", # Path in the checkout to the docs root
}
