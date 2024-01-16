# HSE_MLDS_project_bigdata

Проект по Big Data на тему: Telegram Bot для своевременного уведомления пользователей о появлении новых билетов в Большом театре.

# Полезность

Бот имеет наибольшую полезность в период праздников, особенно под Новый год, когда есть большой спрос на популярные представления (например, "Щелкунчик"), на которые театр открывает продажи только в определенные дни и время. Цель нашего бота оповещать пользователя об изменении количества и цены билетов интересующих его спектаклей. 

# Структура проекта

В данном проекте реализована система, которая:

1. производит регулярную загрузку данных c [сайта Большого театра](https://bolshoi.ru/timetable/all) в хранилище;
2. обрабатывает эти данные в хранилище;
3. отправляет уведомления об измениях в Telegram Bot;
4. построение графиков с аналитикой в Yandex Datalens.


# Компоненты системы
