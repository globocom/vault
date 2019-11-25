.PHONY: help clean setup run pycodestyle tests tests_ci migrations_test check-env-vars

CWD="`pwd`"
PROJECT_NAME = vault
PROJECT_HOME = $(CWD)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Clear *.pyc files, etc
	@echo "Cleaning up"
	@find . -name "*.pyc" -delete
	@find . -name "*.~" -delete

dependencies: ## Install project dependencies
	@echo "Installing dependencies"
	@pip install -r $(PROJECT_HOME)/requirements_test.txt	

setup: dependencies ## Install project dependencies and some git hooks
	@echo "Adding git hooks..."
	@cp ./helpers/git-hooks/pre-commit ./.git/hooks/pre-commit
	@chmod ug+x ./.git/hooks/pre-commit

pycodestyle: ## Check source-code for pycodestyle compliance
	@echo "Checking source-code pycodestyle compliance"
	@-pycodestyle $(PROJECT_HOME) --ignore=E501,E126,E127,E128,W605

migrations_test: ## Fill test database
	@python manage.py makemigrations --settings=vault.settings_test
	@python manage.py migrate --settings=vault.settings_test

tests: migrations_test clean pycodestyle ## Run all tests with coverage
	@echo "Running all tests with coverage"
	@py.test --cov-config .coveragerc --cov $(PROJECT_HOME) --cov-report term-missing

tests_ci: migrations_test clean pycodestyle ## Run all tests
	@echo "Running the tests"
	@py.test

run: check-env-vars clean ## Run a Vault development web server
	@python $(PROJECT_HOME)/manage.py runserver 0.0.0.0:8000

reset_dev:
	@tsuru app update -a vaultdev --image-reset

reset_qa:
	@tsuru app update -a vaultqa --image-reset

reset_prod:
	@tsuru app update -a vault --image-reset

deploy_dev: build_tag
	@tsuru app-deploy . -a vaultdev

deploy_qa: build_tag
	@tsuru app-deploy . -a vaultqa

deploy_prod: build_tag
	@tsuru app-deploy . -a vault

build_tag:
	./build_tag.sh

check-env-vars:
ifndef VAULT_KEYSTONE_PROJECT
	$(error VAULT_KEYSTONE_PROJECT is undefined)
endif

ifndef VAULT_KEYSTONE_USERNAME
	$(error VAULT_KEYSTONE_USERNAME is undefined)
endif

ifndef VAULT_KEYSTONE_PASSWORD
	$(error VAULT_KEYSTONE_PASSWORD is undefined)
endif
