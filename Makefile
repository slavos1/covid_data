SHELL = bash
VENV ?= .venv

all: get_phe_data show

get_phe_data:
	time -p curl -s -o >(jq -r '' > daily_cases.json) "https://coronavirus.data.gov.uk/api/v1/data?filters=areaType=overview&structure=%7B%22date%22:%22date%22,%22newCasesByPublishDate%22:%22newCasesByPublishDate%22%7D&format=json" --compressed

show:
	${VENV}/bin/python show.py

