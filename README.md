Тестовое задание для Aviata.kz

Для запуска приложения необходимо установить зависимости(requirements.txt, redis, rabbitmq) и запустить из корня проекта supervisord. Сервер запускается по адресу localhost:8889

В файле tasks/tasks.py находятся функции обновления кэша и проверки стоимости билетов.

Кэш состоит из 2 частей:
1) Для каждого направления в редисе есть хэш, в котором хранятся токены самых дешевых билетов на месяц вперед. Название хэша - это название направления. Ключ внутри хэша - это дата, а значение - токен самого дешевого билета на эту дату
2) Хэши для хранения информации по конкретному билету. Название хэша - "flight:token", где token - это токен билета.Ключи внутри хэша - from_city, to_city, date, price, is_checked, is_valid

Проверить содержимое кэша можно с помощью api функций api/get_direction_hash и api/get_flights_cache

Для того чтобы не ждать таймингов, я добавил функции для ручного запуска обновления кэша(api/update_cache) и проверки билетов(api/check_flights)