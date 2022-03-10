YaTube
=====

Описание проекта
----------
Социальная сеть для авторов и подписчиков. Пользователи могут подписываться на избранных авторов, оставлять и удалять комментари к постам, оставлять новые посты на главной странице и в тематических группах, прикреплять изображения к публикуемым постам. 

Проект реализован на MVT-архитектуре, реализована система регистрации новых пользователей, восстановление паролей пользователей через почту, система тестирования проекта на unittest, пагинация постов и кэширование страниц. Проект имеет верстку с адаптацией под размер экрана устройства пользователя.

Системные требования
----------
* Python 3.8+
* Works on Linux, Windows, macOS, BSD

Стек технологий
----------
* Python 3.8
* Django 2.2 
* Unittest
* Pytest
* SQLite3
* CSS
* JS
* HTML

Размещение проекта
----------
Проект работает и запущен на боевом сервере Яндекс.Облако на базе веб-серевера nginx и gunicorm под Ubuntu 20.04 lts с БД PostgreSQL. 

[Ссылка на сайт размещенного проекта](https://nikitachalykh.ddns.net/)

Установка проекта из репозитория (Linux и macOS)
----------

1. Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone 'https://github.com/NikitaChalykh/YaTube.git'

cd YaTube
```
2. Cоздать и активировать виртуальное окружение:
```bash
python3 -m venv env

source env/bin/activate
```
3. Установить зависимости из файла ```requirements.txt```:
```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```
4. Выполнить миграции:
```bash
cd hw05_final

python3 manage.py migrate
```
5. Запустить проект (в режиме сервера Django):
```bash
python3 manage.py runserver
```

Развитие проекта
----------
Проект находится в стадии развития, есть планы по расширению функциональности: добавления поддержки GIF-анимаций, коротких видео и возможности вставки ссылок на YouTube с предпросмотром. 
