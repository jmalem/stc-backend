SHELL := /bin/bash


# Verbose quiet, etc
Q := $(if $V,,@)
M = $(shell printf "\033[34;1m▶\033[0m")

.PHONY: run lib* data*

current_dir=$(CURDIR)

run:
	python3 main.py

lib.gen:
	$Q pip3 freeze > requirements.txt
	$(info $(M) Generated a new requirement.txt)

lib.install:
	pip3 install -r requirements.txt

data:
	$Q mdb-export -Q -d '|' HS-toys.mdb Swatch1 > ${current_dir}/data/data.csv 2>&1
	$(info $(M) Generated data/data.csv)