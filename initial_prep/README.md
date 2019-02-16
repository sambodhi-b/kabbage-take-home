# Development Platform
* OS: Windows 10 with Ubuntu WSL
* Version Management: Git installed on Ubuntu WSL
* Container Platform: Docker Engine installed on Win 10; Docker Client installed on Ubuntu WSL linked to Windows Docker Engine
* Python: Python 2.7.15rc1 installed on Ubuntu WSL
* Python Package Manangement: pipenv

# Pipenv Set-Up
1. On Project Root, ran; ```pipenv --two```
2. Install Essential Packages:  
    2.1. Scikit-Learn: ```pipenv install scikit-learn```
3. Install Packages Helpful for Development:  
    3.1. Jupyter: ```pipenv install --dev jupyter```

# Starting Jupyter Notebook
```
pipenv run jupyter notebook --no-browser
```

# Analysis and Cleanup
**Please see ['initial_analysis_and_cleanup.ipynb'](initial_analysis_and_cleanup.ipynb) for details** 