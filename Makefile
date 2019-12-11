.PHONY: help clean deps setup pycodestyle migrations-test tests tests-ci run docker-up docker-down docker-clean

CWD="`pwd`"
PROJECT_NAME = vault
PROJECT_HOME = $(CWD)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Project cleaning up for any extra files created during execution
	@echo "Cleaning up"
	@find . -name "*.pyc" -delete
	@find . -name "*.~" -delete

deps: ## Install project dependencies
	@echo "Installing dependencies"
	@pip install -r $(PROJECT_HOME)/requirements_test.txt

setup: dependencies ## Install project dependencies and some git hooks
	@echo "Adding git hooks..."
	@cp ./helpers/git-hooks/pre-commit ./.git/hooks/pre-commit
	@chmod ug+x ./.git/hooks/pre-commit

pycodestyle: ## Check source-code for pycodestyle compliance
	@echo "Checking source-code pycodestyle compliance"
	@-pycodestyle $(PROJECT_HOME) --ignore=E501,E126,E127,E128,W605

migrations-test: ## Database test migrations
	@python manage.py makemigrations --settings=vault.settings_test
	@python manage.py migrate --settings=vault.settings_test

tests: migrations-test clean pycodestyle ## Run tests (with coverage)
	@echo "Running all tests with coverage"
	@py.test --cov-config .coveragerc --cov $(PROJECT_HOME) --cov-report term-missing

tests-ci: migrations-test clean pycodestyle ## Run tests
	@echo "Running the tests"
	@py.test

run: clean ## Run a project development web server
	@python $(PROJECT_HOME)/manage.py runserver 0.0.0.0:8000

docker-shell: ## Open a shell inside vault_app container
	@docker exec -it vault_app /bin/bash

docker-clean: ## Remove any container, network, volume and image created by docker
	@docker-compose down -v --rmi all --remove-orphans

