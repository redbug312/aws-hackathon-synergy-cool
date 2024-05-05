ifeq ($(OS), Windows_NT)
    PYTHON3 ?= python
    ENV ?= . $(shell pwd)/venv/scripts/activate; \
        PYTHONPATH=$(shell pwd) \
        PATH=/c/Program\ Files\ \(x86\)/NSIS/:$$PATH
else
    PYTHON3 ?= python3
    ENV ?= . $(shell pwd)/venv/bin/activate; \
        PYTHONPATH=$(shell pwd)
endif

.PHONY: lint
lint: venv
	$(ENV) pycodestyle src test --ignore=E501

venv: src/generate-recommendations/requirements.txt
	virtualenv -p $(PYTHON3) venv
	$(ENV) $(PYTHON3) -m pip install -r $^
	touch $@  # update timestamp
