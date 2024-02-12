db_up:
	docker-compose up --remove-orphans -d

db_down:
	docker-compose down

makemg:
	docker-compose run api python manage.py makemigrations

mg:
	docker-compose run api python manage.py migrate

create_admin:
	docker-compose run api python manage.py createsuperuser

local_start:
	python manage.py runserver

start:
	docker-compose up --remove-orphans -d

docker_m:
	docker-compose exec python manage.py migrate

build:
	docker-compose build

initial_setup:
	docker-compose up --no-deps -d postgres
	docker-compose build --no-cache
	make start
	make mg

