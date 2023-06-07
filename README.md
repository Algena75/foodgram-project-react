# Проект Foodgram
Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

![foodgram_workflow.yml](https://github.com/Algena75/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Команда разработчиков:
Когорта 19+ и
Алексей Наумов

## Проект развернут на сервере:
```
http://algena.ddns.net/
```

Документация по api:

```
http://algena.ddns.net/api/docs/
```

Администрирование (для входа использовать e-mail: admin@admin.com , password: admin):

```
http://algena.ddns.net/admin/
```

## Используемые технолологии:

Django v.2.2

djangorestframework v.3.12.4

PyJWT v.2.1.0

PostgreSQL 13.0

Docker 23.0.4

NGINX + Gunicorn

GitActions

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Algena75/foodgram-project-react.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Перейдите в директорию /backend/ и установите зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Установите Docker и Docker Compose:

```
sudo apt install docker-ce docker-compose -y
```

Перейдите в директорию ../infra/. В файле .env необходимо указать переменные окружения для доступа к БД.
Соберите контейнеры:

```
docker-compose up -d (для пересборки добавьте параметр --build)
```

После сборки и запуска контейнеров выполните скрипт для запуска базы данных проекта:

```
docker-compose exec backend python manage.py start_db
```
