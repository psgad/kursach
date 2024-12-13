from commands import *
from api import *
from bd import BD
from main import admin_users


bd = BD()

print(bd.selectBD('users'))
print(admin_users())