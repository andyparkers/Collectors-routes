# Collectors Routes

## Описание

Программа для оптимизации маршрутов инкассаторов в Москве. В городе размещено множество банкоматов с двумя бункерами: для приема и выдачи. Задача состоит в расчете ежедневных маршрутов для групп инкассаторов так, чтобы не возникало ситуаций, когда бункер для приема переполняется или для выдачи опустеет. Для расчета используются статистические характеристики количества банкнот и размеры бункеров каждого банкомата, которые предполагаются одинаковыми на каждый день.

1. Количество групп инкассаторов: 5.
2. Количество банкоматов: 1000.
3. Маршрут строится на несколько дней вперед.
4. Перемещение между банкоматами происходит по дорожной сетке. Время перемещения задается статистическими характеристиками.
5. Рабочий день инкассаторов не превышает 8 часов.
6. Не обязательно каждый день обслуживать все банкоматы.
7. На экран выводится информация о маршрутах инкассаторов на каждый день.

## Стек технологий

- Python
- MySQL
- Folium

## Модули программы

- **atms_classes.py**: содержит классы Atm, MoscowCollectors, MoscowAtms, Collector, данные о границах области, в которой расположены банкоматы, а также места расположения коллекторов (статичные стартовые точки).
- **client.py**: клиентское GUI для взаимодействия с сервером.
- **database.py**: функции для взаимодействия с БД: получение данных о банкомате, изменение параметров банкомата, добавление кортежа.
- **db_config.py**: данные для подключения к БД: адрес хоста, логин, пароль, имя таблицы.
- **geoapi.py**: взаимодействие с API для получения маршрутов на основе географических координат.
- **gui.py**: GUI для сервера, моделирующий работу инкассаторов на несколько дней.
- **main.py**: backend-логика сервера для получения маршрутов на несколько дней и отправки их клиенту.
- **utility.py**: вспомогательные функции, такие как вычисление расстояния между координатами и отправка данных клиенту.

## Параметры моделирования

- Количество банкоматов: 1000 шт.
- Количество групп инкассаторов: 5 шт.
- Территориальные ограничения: г. Москва.
- Ёмкость отсеков под принимаемые и выдаваемые купюры: 8000 шт.
- Показатели дисперсии и матожидания по получению/выдаче купюр в сутки: D(x) = 25, M(x) = 235.
- Время обслуживания банкомата подчиняется нормальному закону распределения с M(x) = 12 и δ = 3.
- Рабочий день инкассаторов ограничен 480 минутами.
- Количество обслуживаемых банкоматов в день 5-ю инкассаторами: 50 шт.

## База данных

В качестве БД использовалась MySQL. Ниже приведено содержание таблицы.

![Таблица](ссылка_на_картинку)

### Атрибуты таблицы:

- Id банкомата;
- Долгота банкомата;
- Широта банкомата;
- Референсное значение ёмкости хранилищ банкомата;
- Текущее значение ёмкости хранилища принятых банкоматом купюр;
- Текущее значение ёмкости хранилища выдаваемых банкоматом купюр;
- Значение дисперсии расхода купюр за день;
- Значение математического ожидания расхода купюр за день.
## Графический интерфейс пользователя

![Кнопка запроса](ссылка_на_картинку_1)

Клиент может отправить запрос серверу на получение HTML-файлов для их дальнейшей отрисовки в GUI клиента, для этого нужно нажать кнопку.

![Выбор дня моделирования](ссылка_на_картинку_2)

Также клиент может выбрать, карту какого дня моделирования он хочет увидеть, с помощью соответствующих элементов.

![Заглушка](ссылка_на_картинку_3)

Если по какой-либо причине данных об N-ной карте у клиента нет, будет показана "заглушка".

## UML Sequence Diagram

![UML Sequence Diagram](ссылка_на_картинку_4)


