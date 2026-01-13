КАК ЗАПУСКАТЬ ПРОЕКТ:

1. Терминале пишем; cd gamebuy

   2. Создать виртуальное окружение
python -m venv venv

3. Активировать виртуальное окружение

Windows:

venv\Scripts\activate


Mac/Linux:

source venv/bin/activate

4. Установить зависимости
pip install -r requirements.txt

5. Сделать миграции
python manage.py makemigrations
python manage.py migrate

6. Запустить сервер
python manage.py runserver
