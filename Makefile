# -*- mode: makefile; -*-

UNAME := $(shell uname -s)
CONTAINER_RUNTIME = $(shell command -v podman 2> /dev/null || echo docker)
DOXYGEN = doxygen
OPEN = $(shell which xdg-open || which gnome-open || which open)
PYTHON = /usr/bin/env python3
PIPARG = # e.g., --user
PIP = $(PYTHON) -m pip $(PIPARG)
PYTEST = /usr/bin/env pytest
R = /usr/bin/env R --no-save --no-restore
GIT = git
CMAKE = /usr/bin/env cmake
SELF_DIR = $(dir $(lastword $(MAKEFILE_LIST)))
GETVER = $(abspath $(SELF_DIR))/getrversion.py
LINTER = cclint
NINJA := $(shell command -v ninja 2> /dev/null)
NINJA_BUILD_OPT = -v
FINDEXEC :=
ifeq ($(UNAME),Darwin)
  FINDEXEC +=  -perm +111
else
  FINDEXEC +=  -executable
endif


PKG = kvaser

default: install
	@echo "-----------------------"
	@$(PYTHON) -m $(PKG)

.PHONY: update
update:
	$(PIP) install wheel setuptools twine --upgrade

UID := $(shell id -u)
PWD := $(shell pwd)
.PHONY: build source
DOCKERRUN = $(CONTAINER_RUNTIME) run -ti --rm --privileged --user $(UID):0 --network=host -v $(PWD):/io buildmany

build: clean
	$(PYTHON) setup.py bdist_wheel -d dist
	$(MAKE) source

source:
	$(PYTHON) setup.py sdist

.PHONY: clean
clean:
	@rm -Rf dist/* *.egg-info build *.so *.so.* src/*.egg-info tests/bin/*

.PHONY: upload_test
upload_test:

	$(PYTHON) -m twine upload --repository pypitest dist/*
.PHONY: upload
upload:	source
	$(PYTHON) -m twine upload dist/* --verbose --repository-url https://upload.pypi.org/legacy/

.PHONY: uninstall
uninstall:
	$(PIP) uninstall $(PKG) -y

.PHONY: install
install: uninstall
	$(PYTHON) setup.py install
	rm -Rf *.egg-info

.PHONY: installdev
installdev:
	$(PIP) install -e .

.PHONY: check
check:
	$(PYTHON) setup.py flake8

.PHONY: test
test:
	$(PYTHON) setup.py test

.PHONY: cov
cov: coverage
	@$(OPEN) tests/htmlcov/index.html

.PHONY: coverage
coverage:
	pytest --cov=kvaser tests/ --cov-report=html:tests/htmlcov $(TESTOPT)

.PHONY: installpypi_test
installpypi_test:
	$(PIP) install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ${PKG}

.PHONY: installpypi
installpypi: uninstall
	$(PIP) install --upgrade $(PKG) --no-binary :all:

################################################################################

.PHONY: markdown
markdown:
	@if [ -z "command -v grip" ]; then \
	echo "Install dependency: pip install grip"; \
	else grip 1313 -b; fi

.PHONY: doc
doc:
	@cd doc; $(MAKE) html

.PHONY: d
d: doc
	@open doc/build/html/index.html

################################################################################

.PHONY: dockerbuild
dockerbuild:
	$(CONTAINER_RUNTIME) build  --build-arg UID=${UID} --network=host . -t target_test

.PHONY: docker
docker:
	$(CONTAINER_RUNTIME) run -ti --rm --privileged --network=host -v $(PWD):/io target_test bash

DOCKERTEST=kkholst/stat:python
.PHONY: dockertest
dockertest:
	$(CONTAINER_RUNTIME) run -ti --rm --privileged --network=host -u 0:0 -v $(PWD):/data ${DOCKERTEST} bash
