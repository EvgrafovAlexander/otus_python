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
- Run python manage.py makemigrations to create migrations for those changes
- Run python manage.py migrate to apply those changes to the database.

