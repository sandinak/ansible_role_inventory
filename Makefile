# handle per OS config
UNAME_S 						:= $(shell uname -s)
UNAME 							:= $(shell uname | tr '[:upper:]' '[:lower:]')
KERNEL_VER 						:= $(shell uname -a | cut -d' ' -f 3)
ROOT_DIR						:= $(PWD)
PLAYBOOKS_DIR 					:= $(ROOT_DIR)/ansible/playbooks
VENV_DIR						:= $(ROOT_DIR)/venv
HOSTNAME 						:= $(shell hostname)

# version of python
ENVIRONMENTS = all

help:
	@echo "Make targets:"
	@echo "  help         - this help"
	@echo "  all          - build all the things"
	@echo "  env          - working ansible environment"
	@echo "  clean        - remove build and env"

.DEFAULT_GOAL := all

# environment
SHELL := /bin/bash

# virtualenv
PYTHON_BIN      	:= $(shell which python3)
ACTIVATE_BIN 	  	:= venv/bin/activate
PIP_BIN 			:= venv/bin/pip

# target for running
all: env 

env: venv 
clean:
	@$(RM) -r venv; \
	find . -name "*.pyc" -exec $(RM) -rf {} \;

# handle VENV
venv: $(VENV_DIR) venv/touchfile 

$(VENV_DIR): requirements.txt
	@echo "building venv"
	@test -d venv || virtualenv -p $(PYTHON_BIN) venv
	@. venv/bin/activate; PYTHONWARNINGS='ignore:DEPRECATION' LANG=en_US.UTF-8 pip install --upgrade pip
	@. venv/bin/activate; PYTHONWARNINGS='ignore:DEPRECATION' LANG=en_US.UTF-8 pip install -r requirements.txt

venv/touchfile:
	@touch venv/touchfile