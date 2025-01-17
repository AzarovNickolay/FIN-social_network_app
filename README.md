# Проектная работа по разработке БД для социальной сети с использованием нереляцилонной БД *MongoDB*

## Описание:
Репозиторий содержит набор файлов для разворачивания FastAPI-приложения для проведения операций над БД социальной сети через API с использованием HTTP-Запросов.

## Установка:
Для локальной установки требуется:
 - В директории с файлами проекта совершить сборку образа приложения через ```docker-compose build```
 - Произвести запуск контейнера с образом через ```docker-compose up```

После завершения сборки и запуска контейнера FastAPI приложение будет доступно на http://localhost:8000/ 

*При необходимости изменить порт требуется перед сборкой образа отредактировать ```dockerfile```, указав желаемый порт*

## Работа с приложением:
В приложении реализованы запросы, позволяющие реализовывать следующие CRUD-Операции с БД:
 - Добавить пользователя
 - Добавить пост
 - Найти всех пользователей
 - Найти пользователя по имени пользователя
 - Найти пользователей с более чем 100 друзьями.
 - Подсчитать количество пользователей в сети.
 - Найти все посты конкретного пользователя.
 - Найти посты, которые получили более 50 лайков.
 - Обновить адрес электронной почты пользователя по имени пользователя.
 - Добавить нового друга к пользователю.
 - Удалить пользователя по ID.
 - Найти пользователей, зарегистрированных после определенной даты.
 - Найти посты, содержащие слово "встреча".
 - Найти пользователей, у которых есть общие друзья с заданным пользователем.
 - Найти посты с определенным количеством лайков и комментариев.
 - Найти пользователей с определенным доменом электронной почты.
 - Подсчитать количество постов каждого пользователя.

После запуска приложения swagger-документация по реализованным эндпоинтам с подробным описанием доступна на http://localhost:8000/docs


## Тестовые данные:
Для наполнения БД тестовыми данными может быть использован скрипт ```mock_data_maker.py```, который добавляет данные в коллекции ```Users``` и ```Posts```. Скрипт может быть запущен на локальной машине после запуска контейнера с приложением.
