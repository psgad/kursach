import psycopg2
import psycopg2.extras
import json
from config import HOST, USER, PASSWORD, DATABASE

class BD:
    def __init__(self):
        """
        Инициализация соединения с базой данных.
        """
        self.connect = psycopg2.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
        )
        self.connect.autocommit = True

    def __del__(self):
        """
        Закрытие соединения при удалении объекта.
        """
        if self.connect:
            self.connect.close()

    def execute_query(self, query, params=None):
        """
        Выполняет SQL-запрос.
        :param query: SQL-запрос.
        :param params: Параметры запроса (по умолчанию None).
        :return: Результат выполнения запроса (если есть).
        """
        with self.connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, params)
            if cursor.description:  # Проверка, если запрос возвращает данные
                return cursor.fetchall()

    def inputBD(self, table, **kwargs):
        """
        Вставляет данные в таблицу.
        :param table: Название таблицы.
        :param kwargs: Данные для вставки (ключ - название колонки, значение - значение).
        """
        columns = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({values});"
        
        self.execute_query(query, list(kwargs.values()))

    def selectBD(self, table, limit=None, offset=None):
        """
        Выполняет SELECT-запрос.
        :param table: Название таблицы.
        :param limit: Ограничение количества строк (по умолчанию None).
        :param offset: Смещение строк (по умолчанию None).
        :return: Результат выполнения запроса в формате JSON.
        """
        query = f"SELECT * FROM {table}"
        
        if limit is not None and offset is not None:
            query += f" LIMIT {limit} OFFSET {offset}"
            
        result = self.execute_query(query)
        
        return json.loads(json.dumps([dict(row) for row in result], ensure_ascii=False, default=str))

    def oneSelectBD(self, table, where_data):
        """
        Выполняет SELECT-запрос для получения одной строки по нескольким условиям.
        :param table: Название таблицы.
        :param where_data: Словарь с условиями для фильтрации (ключ - название колонки, значение - значение для сравнения).
        :return: Одна строка из таблицы, соответствующая условиям, или None, если строка не найдена.
        """
        where_clauses = [f"{column} = %s" for column in where_data.keys()]
        where_clause = " AND ".join(where_clauses)

        query = f"SELECT * FROM {table} WHERE {where_clause};"

        result = self.execute_query(query, list(where_data.values()))

        return result[0] if result else None

    def updateBD(self, table, set_data, where_data):
        """
        Выполняет UPDATE-запрос с возможностью обновления нескольких полей и фильтрации по нескольким условиям.
        :param table: Название таблицы.
        :param set_data: Словарь с данными для обновления (ключ - название колонки, значение - новое значение).
        :param where_data: Словарь с условиями для фильтрации (ключ - название колонки, значение - значение для сравнения).
        """
        set_clauses = [f"{column} = %s" for column in set_data.keys()]
        set_clause = ", ".join(set_clauses)

        where_clauses = [f"{column} = %s" for column in where_data.keys()]
        where_clause = " AND ".join(where_clauses)

        query = f"""
        UPDATE {table} SET {set_clause} WHERE {where_clause};
        """
        
        params = list(set_data.values()) + list(where_data.values())
        print(query)
        print()
        print(params)
        self.execute_query(query, params)

    def deleteBD(self, table, **kwargs):
        """
        Выполняет DELETE-запрос с возможностью удаления по нескольким полям.
        :param table: Название таблицы.
        :param kwargs: Условия для удаления (ключ - название колонки, значение - значение).
        """
        conditions = [f"{column} = %s" for column in kwargs.keys()]
        where_clause = " AND ".join(conditions)

        query = f"DELETE FROM {table} WHERE {where_clause};"
        self.execute_query(query, list(kwargs.values()))
