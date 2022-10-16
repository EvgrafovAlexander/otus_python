# Django Tutorial
https://docs.djangoproject.com/en/4.1/intro/tutorial01/


### run server
```python3 manage.py runserver 8080```

### create app
```python3 manage.py startapp polls```

### migrations
```python3 manage.py makemigrations polls```

```python3 manage.py migrate```

#### При необходимости добавления/изменения моделей:
- Change your models (in models.py).
- Run python3 manage.py makemigrations to create migrations for those changes
- Run python3 manage.py migrate to apply those changes to the database.

### Отобразить sql-скрипт миграции
```python3 manage.py sqlmigrate polls 0001```

### Проверка на наличие проблем в проекте
```python3 manage.py check```

### Запуск интерактивной оболочки
```python3 manage.py shell```

### Creating an admin user
```python3 manage.py createsuperuser```

admin admin@example.com admin

### Use generic views:
- Convert the URLconf.
- Delete some of the old, unneeded views.
- Introduce new views based on Django’s generic views.

### run tests
```python3 manage.py test polls```

### Good rules-of-thumb include having:
- a separate TestClass for each model or view
- a separate test method for each set of conditions you want to test
- test method names that describe their function