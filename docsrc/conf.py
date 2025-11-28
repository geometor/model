from photon_platform.publish.global_conf import *
import geometor.model as module

version = module.__version__

org = "geometor"
org_name = "GEOMETOR"

repo = "model"
repo_name = "model"

setup_globals(org, org_name, repo, repo_name)

""" autoapi_options = [
    "members",
    "undoc-members",
    # "private-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
    "inherited-members",
]

autoapi_keep_files = True


import os
import tomllib

# Dynamically determine autoapi_dirs from pyproject.toml
# Use __file__ to determine the location of conf.py (docsrc/conf.py)
# Project root is one level up from docsrc
conf_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(conf_dir, '..'))
pyproject_path = os.path.join(project_root, 'pyproject.toml')

with open(pyproject_path, 'rb') as f:
    pyproject_data = tomllib.load(f)

# Extract package configuration
# Assuming setuptools configuration structure
try:
    find_config = pyproject_data['tool']['setuptools']['packages']['find']
    where = find_config.get('where', ['.'])[0]  # Default to current dir if not specified
    include = find_config.get('include', ['*'])[0] # Default to all if not specified
    
    # Construct the path: project_root / where / include
    # Note: 'include' might be a list of patterns, here we assume the first one is the main package directory
    # if it matches a directory name.
    # For geometor.model, where=['src'], include=['geometor']
    
    # autoapi expects the path to the *source* code. 
    # If we point to 'src/geometor', autoapi will see 'geometor' as the top level.
    # If we point to 'src', autoapi might see 'geometor' as a subpackage if implicit namespaces work.
    # The previous working config was '../src/geometor'.
    
    # Let's construct the path based on the previous working state:
    # ../src/geometor
    
    autoapi_dirs = [os.path.join(project_root, where, include)]
    
except KeyError as e:
    print(f"Warning: Could not parse pyproject.toml for autoapi_dirs: {e}")
    # Fallback to default if parsing fails
    autoapi_dirs = [os.path.abspath('../src/geometor')]

print(f"AutoAPI Dirs: {autoapi_dirs}")
autoapi_root = 'modules/api'
autoapi_python_use_implicit_namespaces = True """
