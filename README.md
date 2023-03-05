   **Foodgram** - Проект Foodgram «Продуктовый помощник».На этом сервисе пользователи смогут публиковать рецепты,
   подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное»,
   а перед походом в магазин скачивать сводный список продуктов,
   необходимых для приготовления одного или нескольких выбранных блюд.
___
### **Что внутри**:
* Поддерживает все типовые операции CRUD
* Предоставляет данные в формате JSON
* Аутентификация по Jwt-токену
* Реализованы пермишены, фильтрации, пагинация ответов от API
___

### **Пользовательские роли**:
* **Аутентифицированный пользователь (user)** — может, как и Аноним, читать всё, дополнительно он может публиковать рецепты и подписываться на других авторов.  Роль присваивается по умолчанию каждому новому пользователю.
* **Администратор (admin)** — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры, а так же назначать роли пользователям.

___
### **Как запустить проект**:

* Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:Vediusse/infra_sp2.git
cd backend
```

### **Шаблон наполнения env-файла:**:
1) Шаблон наполнения .env должен быть расположен по пути infra/.env :
    ```
   DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
   DB_NAME=postgres # имя базы данных
   POSTGRES_USER=postgres # логин для подключения к базе данных
   POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
   DB_HOST=db # название сервиса (контейнера)
   DB_PORT=5432
   ```


### **Как запустит проект**:
1) Поднимаем контейнеры :
   ```
   docker-compose up -d --build
   ```
2) Выполняем миграции:
   ```
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```
3) Подгружаем статику:
   ```
   docker-compose exec web python manage.py collectstatic --no-input
   ```
4) Создаем дамп базы данных:
   ```
   docker-compose exec web python manage.py dumpdata > dump.json
   ```
5) Останавливаем контейнеры: 
   ```
   docker-compose down -v
   ```
* Отправка email 
```
    1) Зайти в файл settings
    2) Исправить переменные
        EMAIL_HOST_USER = 'example@domen.ru'
        EMAIL_HOST_PASSWORD = 'Пароль приложения'
        EMAIL_HOST 
        EMAIL_PORT 
        EMAIL_USE_TLS = True/False
        EMAIL_USE_SSL = False/False
        (можно получить на сайте сервиса электронной почты )
ИЛИ
    Заменить 
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    На
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
* Для заполнения базы данных:
```
    python import_csv
```
* Запустить проект:
```
python manage.py runserver
```
___
### **Примеры запросов**:
* GET-запрос возвращает список всех пользователей:
```
http://localhost:8000/api/users/
```
```
"count": 1,
    "next": "http://localhost:8000/api/recipes/?limit=10&offset=10",
    "previous": null,
    "results": [
        {
            "id": 1,
            "ingredients": [
                {
                    "id": 1,
                    "name": "супец",
                    "measurement_unit": "г",
                    "amount": 7
                }
            ],
            "tags": [
                1
            ],
            "image": "http://localhost:8000/media/recipes/images/039d17a0-1a65-4ead-9d43-bdc2be91b648.png",
            "name": "SDGSDGSDGSDG",
            "text": "fdfsdfa",
            "cooking_time": 1,
            "author": {
                "id": 1,
                "username": "example",
                "email": "example@yandex.ru",
                "first_name": "",
                "last_name": "",
                "is_subscribed": false
            }
        },
      ]
}
```
* GET-запрос возвращает рецепт по id:
```
http://localhost:8000/api/recipes/10/
```
```
{
    "id": 10,
    "ingredients": [
        {
            "id": 1,
            "name": "супец",
            "measurement_unit": "г",
            "amount": 0
        }
    ],
    "tags": [
        1
    ],
    "image": "http://localhost:8000/media/recipes/images/ddd6b491-97eb-4d1a-ab4c-ac86c73d0df5.png",
    "name": "SDGSDGSDGSDG",
    "text": "крутой супе",
    "cooking_time": 1,
    "author": {
        "id": 1,
        "username": "fjjfgaafffacccxszxcggggg",
        "email": "vpupkin@yandex.ru111",
        "first_name": "",
        "last_name": "",
        "is_subscribed": false
    }
}
```
* Остальные пример запросов можно посмотреть по [ссылке](http://127.0.0.1:8000/api/redoc/) после запуска проек
* Автор
Работяги из ЯП

* [Рублёв Валерий](https://github.com/Vediusse) 

