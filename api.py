import bs4
import requests
from commands import *
from config import HEADERS

URL = 'https://mpt.ru/'

WEEKDAYS = {
    0: "ПОНЕДЕЛЬНИК",
    1: "ВТОРНИК",
    2: "СРЕДА",
    3: "ЧЕТВЕРГ",
    4: "ПЯТНИЦА",
    5: "СУББОТА",
    6: "ВОСКРЕСЕНЬЕ"
}

def get_soup(url, headers):
    """
    Функция, создающая запрос на сайт и возвращающая объект BeautifulSoup.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Проверка на ошибки HTTP
    return bs4.BeautifulSoup(response.text, 'html.parser')

def zamena_group():
    """
    Функция, позволяющая спарсить данные с сайта mpt.ru и получить замены на все группы.
    """
    zamena = {}
    tmp = {}
    date = ''
    group = ''
    categories = get_soup('https://mpt.ru/studentu/izmeneniya-v-raspisanii/', HEADERS)
    categories = categories.find('main').find('div', {'class': 'container-fluid text-page'}).find('div', {'class': 'container'}).find_all('div')
    categories = categories[5]
    
    for i in categories.text.split('Группа: '):
        tmp_ = i.split('\n')
        tmps = [j for j in tmp_ if j != '']
        
        if 'Сегодня' in tmps[0]:
            date = int_weekday(datetime.now().weekday())
            zamena[date] = tmp
            tmp = {}
        elif any(day in tmps[0].upper() for day in WEEKDAYS.values()):
            date = next((day for day in WEEKDAYS.values() if day in tmps[0].upper()), None)
            zamena[date] = tmp
            tmp = {}
        else:
            group = tmps[0]
        
        tmps = tmps[5:]
        result = []
        for j in range(0, len(tmps), 4):
            if 'Замены' in tmps[-1]:
                tmps.remove(tmps[-1])
            try:
                result.append({'number': tmps[j], 'before': tmps[j+1], 'after': tmps[j+2].replace('  ', '')})
            except:
                pass
        tmp[group] = result
    
    if len(tmp) > 1:
        zamena[date] = tmp
        zamena[date].pop('')
        return zamena
    else:
        return {}

def chz():
    """
    Функция, которая парсит данные с сайта mpt.ru и определяет числитель/знаменатель недели.
    """
    categories = get_soup(URL + 'studentu/raspisanie-zanyatiy', HEADERS)
    chz = categories.findAll('span')
    for i in chz:
        if i.find(string=True) in ['Знаменатель', 'Числитель']:
            return i.find(string=True)

def pick_all_group():
    """
    Функция, которая парсит данные с сайта mpt.ru и получает расписание всех групп.
    """
    chzm = chz()
    all_groups = {}
    categories = get_soup(URL + 'studentu/raspisanie-zanyatiy', HEADERS)
    blocks = categories.findAll('div', role='tabpanel')
    
    for block in blocks:
        group = block.find('h3').find(string=True).upper()
        tables = block.findAll('table', class_='table table-striped table-hover')
        if len(tables) > 5:
            tables = tables[:5]
        
        bruh = {}
        for table in tables:
            day_week = table.find('h4').find(string=True)
            rezult = []
            rp = table.findAll('td')
            for line_rp in rp:
                if line_rp.find(string=True) == "\n":
                    ch = line_rp.findAll('div')
                    for i in ch:
                        string = " ".join(i.find(string=True).split())
                        rezult.append(string)
                else:
                    if line_rp.find(string=True):
                        rezult.append(line_rp.find(string=True))
            
            rp = rezult
            item = {}
            rr = []
            li = {}
            for i in range(len(rp)):
                if rp[i].isdigit():
                    li[rp[i]] = {}
                elif not rp[i].isdigit() and "." not in rp[i]:
                    if rp[i] == 'ПРАКТИКА':
                        li[list(li.keys())[-1]] = {'ПРАКТИКА': 'препод'}
                    else:
                        if not len(rr) == 2:
                            if li[list(li.keys())[-1]] == {}:
                                rr.append(rp[i])
                elif '.' in rp[i]:
                    if len(rr) == 2:
                        if rr[0] == "":
                            item = {"": "", rr[1]: rp[i]}
                            rr = []
                            li[list(li)[-1]] = item
                        else:
                            item = {rr[0]: rp[i], rr[1]: rp[i+1]}
                            rr = []
                            li[list(li)[-1]] = item
                    elif len(rr) == 1:
                        li[list(li)[-1]] = {rr[0]: rp[i]}
                        rr = []
            bruh[day_week] = li
        all_groups[group[7:]] = bruh
    
    for i in all_groups:
        for j in all_groups[i]:
            for d in all_groups[i][j]:
                if len(all_groups[i][j][d]) == 2:
                    if chzm == "Числитель":
                        all_groups[i][j][d].pop(list(all_groups[i][j][d])[1])
                    else:
                        all_groups[i][j][d].pop(list(all_groups[i][j][d])[0])
    return all_groups

def download():
    """
    Функция, которая вставляет значения замен в полученное расписание.
    """
    rp = pick_all_group()
    zamena = zamena_group()
    for i in zamena:
        for j in zamena[i]:
            for d in zamena[i][j]:
                try:
                    rp[j][i][d['number']] = {"ЗАМЕНА: " + d['after']: ""}
                except:
                    pass
    return rp

def download_json(rp_group):
    """
    Функция, которая преобразует расписание в формат JSON.
    """
    rp = []
    for i in rp_group:
        one_day = {'weekday': i}
        for j in rp_group[i]:
            for d in rp_group[i][j]:
                one_item = {'lesson_number': j, 'lesson_title': d, 'lesson_teacher': rp_group[i][j][d], 'lesson_time': time_of_index(j)}
                one_day[str(j)] = one_item
        rp.append(one_day)
    return rp

if __name__ == '__main__':
    group = download()
    print(download_json(group['П50-7-21']))