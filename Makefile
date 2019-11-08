dev-up:
	docker-compose up

dev-down:
	docker-compose down

build-no-cache:
	./build-run.sh

shell-nginx:
	docker-compose exec nginx  /bin/sh

shell-app:
	docker-compose exec  app /bin/sh

shell-db:
	docker-compose exec  postgres /bin/sh

log-nginx:
	docker-compose logs nginx  

log-app:
	docker-compose logs app

log-db:
	docker-compose logs postgres

collectstatic:
	docker-compose exec app /bin/sh -c "python manage.py collectstatic --noinput"