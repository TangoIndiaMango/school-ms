db_up:
	docker-compose up --remove-orphans -d

db_down:
	docker-compose down

makemg:
	python manage.py makemigrations

mg:
	python manage.py migrate

create_admin:
	python manage.py createsuperuser

start:
	python manage.py runserver