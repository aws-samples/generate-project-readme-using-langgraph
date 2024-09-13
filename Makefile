# Makefile

VENV_NAME?=.venv
PYTHON=${VENV_NAME}/bin/python
PIP=${VENV_NAME}/bin/pip

.PHONY: all venv activate install clean test run help

all: venv install

venv:
	python3 -m venv ${VENV_NAME}

activate:
	@echo "To activate the virtual environment, run:"
	@echo "source ${VENV_NAME}/bin/activate"

install: venv
	${PIP} install .

clean:
	rm -rf ${VENV_NAME}
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

test:
	${PYTHON} -m pytest

help:
	@echo "Available commands:"
	@echo "  make venv      : Create a virtual environment"
	@echo "  make activate  : Show command to activate the virtual environment"
	@echo "  make install   : Install the package and its dependencies"
	@echo "  make clean     : Remove the virtual environment and cache files"
	@echo "  make test      : Run tests"
	@echo "  make all       : Create venv and install package (default)"
	@echo "  make help      : Show this help message"