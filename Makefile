SHELL := /bin/bash

.PHONY: run lib*

run:
	python3 main.py

lib.gen:
	pip3 freeze > requirements.txt

lib.install:
	pip3 install -r requirements.txt