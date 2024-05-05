AWS_DEFAULT_REGION ?= ???
AWS_ACCESS_KEY_ID ?= ???
AWS_SECRET_ACCESS_KEY ?= ???
AWS_SESSION_TOKEN ?= ???

AWS ?= AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
    AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
    AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
    AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN)

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

.PHONY: deploy
deploy: samconfig.toml lint
	$(AWS) sam sync --stack-name sensor-monitoring
	$(AWS) sam deploy

venv: src/generate-recommendations/requirements.txt
	virtualenv -p $(PYTHON3) venv
	$(ENV) $(PYTHON3) -m pip install -r $^
	touch $@  # update timestamp

samconfig.toml:
	$(AWS) sam build
	$(AWS) sam deploy --guided
