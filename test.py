from bd import BD
import datetime


bd = BD()

#print(bd.selectBD('grades', {'user_id':'c43a012f-0954-4bf7-abd1-cd07e13419ed', 'date': datetime.today().strftime('%Y.%m.%d')}))

grades = bd.selectBD('grades', {
    'user_id': 'c43a012f-0954-4bf7-abd1-cd07e13419ed',
    'date': datetime.datetime.today().strftime('%Y.%m.%d')
})
for i in grades:
    print(i['grade'])
