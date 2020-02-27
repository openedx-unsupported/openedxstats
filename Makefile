.PHONY: requirements serve tests upgrade help

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

requirements:  ## execute the requirements
	pip install -r requirements/production.txt

serve:  ## execute the runserver
	python manage.py runserver 0.0.0.0:8000

install-test: ## install requirements for tests
	pip install -r requirements/testing.txt

tests:  ## execute the all tests
	python -Wd -m pytest

export CUSTOM_COMPILE_COMMAND = make upgrade
upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -q -r requirements/pip_tools.txt
	pip-compile --rebuild --upgrade -o requirements/pip_tools.txt requirements/pip_tools.in
	pip-compile --rebuild --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --rebuild --upgrade -o requirements/jenkins.txt requirements/jenkins.in
	pip-compile --rebuild --upgrade -o requirements/testing.txt requirements/testing.in
	pip-compile --rebuild --upgrade -o requirements/production.txt requirements/production.in
static:
	python manage.py collectstatic --noinput

