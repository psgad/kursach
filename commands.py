import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

WEEKDAYS = {
    0: "ПОНЕДЕЛЬНИК",
    1: "ВТОРНИК",
    2: "СРЕДА",
    3: "ЧЕТВЕРГ",
    4: "ПЯТНИЦА",
    5: "СУББОТА",
    6: "ВОСКРЕСЕНЬЕ"
}

LESSON_TIMES = {
    1: '8:30 - 10:00',
    2: '10:10 - 11:40',
    3: '12:00 - 13:30',
    4: '13:50 - 15:20',
    5: '15:30 - 17:00',
    6: '17:10 - 18:40'
}

def read_file(path: str) -> dict:
    """
    Функция, возвращающая прочитанный файл формата json.
    Если файл не существует, создается пустой файл.
    """
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def int_weekday(ch: int) -> str:
    """
    Функция, приводящая число к дню недели.
    Использует словарь для упрощения логики.
    """
    return WEEKDAYS.get(ch, str(ch))

def get_soup(url: str, headers: dict) -> BeautifulSoup:
    """
    Функция, создающая запрос на сайт в зависимости от полученных параметров.
    Возвращает объект BeautifulSoup.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Проверка на ошибки HTTP
    return BeautifulSoup(response.text, 'html.parser')

def write_file(path: str, obj: dict):
    """
    Функция, позволяющая записать json объект в файл формата json.
    """
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(obj, file, indent=4, ensure_ascii=False)

def time_of_index(index: int) -> str:
    """
    Функция, возвращающая промежуток времени для номера пары.
    Использует словарь для упрощения логики.
    """
    return LESSON_TIMES.get(index, '')

def get_today_lessons(lessons: list) -> dict:
    """
    Функция, возвращающая расписание на текущий день.
    Если уроков нет, возвращает None.
    """
    today = int_weekday(datetime.now().weekday())
    for lesson in lessons:
        if lesson['weekday'] == today:
            return lesson
    return None