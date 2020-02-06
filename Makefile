.PHONY: requirements serve tests

requirements:
	pip install -r requirements/production.txt

serve:
	python manage.py runserver 0.0.0.0:8000

install-test: ## install requirements for tests
	pip install -r requirements/testing.txt

tests:
	python manage.py test

