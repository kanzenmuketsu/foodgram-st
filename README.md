-_-
### Для запуска
```bash
cd foodgram-st
docker compose up
docker compose exec itog_backend python manage.py migrate
docker compose exec itog_backend python manage.py collectstatic
docker compose exec itog_backend cp -r /app/collected_static/. /backend_static/static/ 
```
### Для добавления заготовленных ингредиентов
```bash
docker compose exec itog_backend python manage.py loaddata fixture.json
```
### Для добавления супер пользователя
```bash
docker compose exec itog_backend python manage.py createsuperuser
```