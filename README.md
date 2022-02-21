# Описание

Проект на MVT-архитектуре, реализована система регистрации новых пользователей, восстановление паролей пользователей через почту, система тестирования, пагинация постов и кэширование страниц. Проект имеет адаптивную верстку с навигацией по страницам.

# Установка

1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone 'https://github.com/NikitaChalykh/YaTube.git'
```
```
cd YaTube
```
2. Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
3. Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
4. Выполнить миграции:
```
python3 manage.py makemigrations
```
```
python3 manage.py migrate
```
5. Запустить проект:
```
python3 manage.py runserver
```
