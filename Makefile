SHELL:=/bin/bash


no_download: venv
	venv/bin/python bibscraper.py 2>&1 | tee bibscraper.log
	venv/bin/python bibupdater.py sec.bib sec.bib scraped/bibscraped.bib 2>&1 | tee bibupdater.log

donload: venv
	venv/bin/python bibscraper.py -d 2>&1 | tee bibscraper.log
	venv/bin/python bibupdater.py sec.bib sec.bib scraped/bibscraped.bib 2>&1 | tee bibupdater.log

.venv: venv/bin/pip requirements-dev.txt requirements.txt
	venv/bin/pip install -r requirements-dev.txt
	venv/bin/pip install -r requirements.txt
	touch .venv

venv: .venv

venv/bin/pip:
	python3 -m venv venv

.PHONY: download venv no_download
