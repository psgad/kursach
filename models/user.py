from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin):
      data:dict

      def __init__(self, kwargs):
            self.data = kwargs

      def get_id(self):
            return self.data['id']

      def get_data(self): return self.data

      
      def __repr__(self):
            return f'<User {self.username}>'

      
