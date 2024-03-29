.PHONY: all test stop run

all:
	docker-compose up -d

test:
	docker-compose exec -e DJANGO_CONFIGURATION=Test web pytest /app/tests

test_focus:
	docker-compose exec -e DJANGO_CONFIGURATION=Test web pytest -m focus /app/tests

run:
	docker-compose up

stop:
	docker-compose stop

migrate:
	docker-compose exec web python3 manage.py migrate

shell:
	docker-compose exec web bash

pyshell:
	docker-compose exec web python3 manage.py shell

dbshell:
	docker-compose exec web python3 manage.py dbshell

requirements:
	docker-compose exec web pip3 install -r requirements.txt
