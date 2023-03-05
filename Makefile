SHELL := /bin/bash


# Verbose quiet, etc
Q := $(if $V,,@)
M = $(shell printf "\033[34;1m▶\033[0m")

.PHONY: run lib* data* build*

current_dir=$(CURDIR)
table_swatch_1=$(PRODUCT_TABLE_NAME_1)
table_swatch_2=$(PRODUCT_TABLE_NAME_2)
table_swatch_3=$(PRODUCT_TABLE_NAME_3)

run:
	python3 main.py

lib.gen:
	$Q pip3 freeze > requirements.txt
	$(info $(M) Generated a new requirement.txt)

lib.install:
	pip3 install -r requirements.txt

data:
	$Q mdb-export -Q -d '|' ./data/HS-toys.mdb ${table_swatch_1} > ${current_dir}/data/data1.csv 2>&1
	$(info $(M) Generated data/data.csv)
	$Q mdb-export -Q -d '|' ./data/HS-toys.mdb ${table_swatch_2} > ${current_dir}/data/data2.csv 2>&1
	$(info $(M) Generated data/data2.csv)
	$Q mdb-export -Q -d '|' ./data/HS-toys.mdb ${table_swatch_3} > ${current_dir}/data/data3.csv 2>&1
	$(info $(M) Generated data/data3.csv)

clear.data:
	$Q rm ./data/data1.csv ./data/data2.csv ./data/data3.csv ./data/HS-toys.mdb
	$(info $(M) Removed data/data1.csv data/data2.csv data/data3.csv)

build:
	$Q docker-compose --env-file .env up --build