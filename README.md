# Todo-App

## Подготовка
Для работы приложения вам понадобится установленный `Docker` и `Node.js`.

## Запуск приложения
> [!WARNING]
> Перед запуском приложения убедитесь, что у вас запущен Docker. В противном случае `docker compose` упадёт с ошибкой

Поочерёдно вводим следующие команды в терминал:

Создаём .env для приложения:
```bash
cp .env.example .env
  ```

> [!NOTE]
> Значения, копируемые из .env.example уже позволяют поднимать приложение локально.

Поднимаем приложение:
```bash
docker compose up -d
  ```
Приложение поднимется в фоновом режиме, оставляя вам доступ к терминалу.

#### Теперь приложение доступно по адресу http://localhost:3000/

## Остановка приложения
Для обычной остановки контейнеров введите:
```bash
docker compose stop
  ```
Для удаления контейнеров:
```bash
docker compose down
  ```
Для удаления контейнеров вместе с volume:
> [!CAUTION]
> Эта команда удалит все сохранённые данные из бд

```bash
docker compose down -v
  ```


## Тесты
> [!IMPORTANT]
> Все следующие команды вводятся когда контейнеры остановлены/удалены.

> [!WARNING]
> После тестов volume удалится

Для запуска тестов поочерёдно вводим следующие команды:
```bash
cp .env.example .env
docker compose build backend
docker compose up -d --wait db redis
docker compose run --rm backend pytest
docker compose down -v
 ```
> [!TIP]
> Если вы уже копировали .env.example в .env, выполнять эту команду повторно не обязательно

## Стек

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-FF4438?logo=redis&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=white)


#### Frontend взят из стороннего репозитория и не разрабатывался в рамках этого проекта — [makedonsky-it/todo-app-frontend](https://github.com/makedonsky-it/todo-app-frontend)
