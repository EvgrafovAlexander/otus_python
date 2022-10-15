python3 manage.py runserver 8080

### create app
python3 manage.py startapp polls

# run migrations
python3 manage.py migrate

python3 manage.py makemigrations polls

# Отобразить sql-скрипт миграции
python3 manage.py sqlmigrate polls 0001

# Проверка на наличие проблем в проекте
python3 manage.py check

### При необходимости добавления/изменения моделей:
- Change your models (in models.py).
- Run python3 manage.py makemigrations to create migrations for those changes
- Run python3 manage.py migrate to apply those changes to the database.

### Запуск интерактивной оболочки
python3 manage.py shell

### Creating an admin user
python3 manage.py createsuperuser

admin admin@example.com admin

#### Use generic views:
- Convert the URLconf.
- Delete some of the old, unneeded views.
- Introduce new views based on Django’s generic views.
