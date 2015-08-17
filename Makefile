.PHONY: clean setup run pep8 tests

export CFLAGS=-Qunused-arguments
export CPPFLAGS=-Qunused-arguments

CWD="`pwd`"
PROJECT_NAME = vault
PROJECT_HOME = $(CWD)

clean:
	@echo "Cleaning up *.pyc files"
	@find . -name "*.pyc" -delete
	@find . -name "*.~" -delete

setup:
	@echo "Installing dependencies..."
	@pip install -r $(PROJECT_HOME)/requirements_test.txt
	@echo "Adding git hooks..."
	@cp ./helpers/git-hooks/pre-commit ./.git/hooks/pre-commit
	@chmod ug+x ./.git/hooks/pre-commit

run: clean
	@python $(PROJECT_HOME)/manage.py runserver 0.0.0.0:8000

pep8:
	@echo "Checking source-code PEP8 compliance"
	@-pep8 $(PROJECT_HOME) --ignore=E501,E126,E127,E128

tests: clean pep8
	@echo "Running pep8 and all tests with coverage"
	@py.test --cov-config .coveragerc --cov $(PROJECT_HOME) --cov-report term-missing

tests_ci: clean pep8
	@echo "Running pep8 and all tests"
	@py.test
