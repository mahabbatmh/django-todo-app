#!/bin/sh

python manage.py collectstatic --no-input;

python manage.py shell -c "from django.contrib.auth.models import User; \
                           User.objects.filter(username='mahabbatmh').exists() or \
                           User.objects.create_superuser('mahabbatmh',
                           'mahabbatmh@code.edu.az', 'secret_password')" \


wait-for postgres:5432  &&  python manage.py migrate;

if [ "$DEBUG" = "False" ]; then
    gunicorn todoapp.wsgi -b 0.0.0.0:8012 & wait-for rabbitmq:5672 && celery worker --app=todos.tasks;
    else
      python manage.py runserver 0.0.0.0:8012 & wait-for rabbitmq:5672 && celery worker --app=todos.tasks;
fi