.PHONY: requirements serve tests upgrade help

ifdef TOXENV
TOX := tox -- #to isolate each tox environment if TOXENV is defined
endif

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

requirements:  ## execute the requirements
	pip install -r requirements/production.txt

serve:  ## execute the runserver
	python manage.py runserver 0.0.0.0:8000

install-test: ## install requirements for tests
	pip install -r requirements/testing.txt

static:
	$(TOX)python manage.py collectstatic --noinput

tests: static
	$(TOX)python -Wd -m pytest

COMMON_CONSTRAINTS_TXT=requirements/common_constraints.txt
.PHONY: $(COMMON_CONSTRAINTS_TXT)
$(COMMON_CONSTRAINTS_TXT):
	wget https://raw.githubusercontent.com/edx/edx-lint/master/edx_lint/files/common_constraints.txt || touch "$(@)"

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: $(COMMON_CONSTRAINTS_TXT)  ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -q -r requirements/pip_tools.txt
	pip-compile --upgrade -o requirements/travis.txt requirements/travis.in
	pip-compile --rebuild --upgrade -o requirements/pip_tools.txt requirements/pip_tools.in
	pip-compile --rebuild --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --rebuild --upgrade -o requirements/jenkins.txt requirements/jenkins.in
	pip-compile --rebuild --upgrade -o requirements/testing.txt requirements/testing.in
	pip-compile --rebuild --upgrade -o requirements/production.txt requirements/production.in
	# Let tox control the Django version for tests
	grep -e "^django==" requirements/production.txt > requirements/django.txt
	sed '/^[dD]jango==/d' requirements/testing.txt > requirements/test.tmp
	mv requirements/test.tmp requirements/testing.txt
