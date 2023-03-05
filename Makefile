SHELL := /bin/bash


# Verbose quiet, etc
Q := $(if $V,,@)
M = $(shell printf "\033[34;1m▶\033[0m")

.PHONY: run lib* data* build*

current_dir=$(CURDIR)
product_list_table_name=$(PRODUCT_TABLE_NAME)

run:
	python3 main.py

lib.gen:
	$Q pip3 freeze > requirements.txt
	$(info $(M) Generated a new requirement.txt)

lib.install:
	pip3 install -r requirements.txt

data:
	$Q mdb-export -Q -d '|' ./data/HS-toys.mdb ${product_list_table_name} > ${current_dir}/data/data.csv 2>&1
	$(info $(M) Generated data/data.csv)

clear.data:
	$Q rm ./data/data.csv ./data/HS-toys.mdb
	$(info $(M) Removed data/data.csv)

build:
	$Q docker-compose --env-file .env up --build