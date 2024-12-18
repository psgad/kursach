import psycopg2
import psycopg2.extras
from config import HOST, USER, PASSWORD, DATABASE
import os
import datetime

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
        if not os.path.exists('logbd.txt'):
            open('logbd.txt', 'w', encoding='utf-8').write('')

    def __del__(self):
        """
        Закрытие соединения при удалении объекта.
        """
        if self.connect:
            self.connect.close()

    def execute_query(self, query, params=None):
        """
        Выполняет SQL-запрос и возвращает результат.
        :param query: SQL-запрос.
        :param params: Параметры для запроса (по умолчанию None).
        :return: Результат запроса (список строк) и метаданные (названия столбцов).
        """
        cursor = self.connect.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if 'SELECT' in query:
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                with open('logbd.txt', 'a') as file:
                    log = f"""
-----------------------------------------------{datetime.datetime.now()}------------------------------
Поступил запрос на БД: {query}
Данные для ввода: {params}
Результат вывода:
========================================================================================================
{rows}
=========================================================================================================
-----------------------------------------------{datetime.datetime.now()}------------------------------\n\n"""
                    file.write(log)
                return rows, columns

        finally:
            cursor.close()

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

    def selectBD(self, table, where=None, limit=None, offset=None):
        """
        Выполняет SELECT-запрос с возможностью указания условия WHERE, LIMIT и OFFSET.
        :param table: Название таблицы.
        :param where: Условие WHERE в виде словаря (например, {"column1": "value1", "column2": "value2"}). По умолчанию None.
        :param limit: Ограничение количества строк (по умолчанию None).
        :param offset: Смещение строк (по умолчанию None).
        :return: Массив (список) JSON с данными.
        """
        # Формируем базовый запрос
        query = f"SELECT * FROM {table}"

        # Добавляем условие WHERE, если оно есть
        if where is not None:
            where_conditions = []
            for column, value in where.items():
                # Обрабатываем строки и числа
                if isinstance(value, str):
                    where_conditions.append(f"{column} = %s")
                else:
                    where_conditions.append(f"{column} = %s")
            query += " WHERE " + " AND ".join(where_conditions)
            params = list(where.values())
        else:
            params = None

        # Добавляем LIMIT и OFFSET, если они указаны
        if limit is not None and offset is not None:
            query += " LIMIT %s OFFSET %s"
            if params:
                params += [limit, offset]
            else:
                params = [limit, offset]
        elif limit is not None:
            query += " LIMIT %s"
            if params:
                params += [limit]
            else:
                params = [limit]
        elif offset is not None:
            query += " OFFSET %s"
            if params:
                params += [offset]
            else:
                params = [offset]

        # Выполняем запрос
        result, columns = self.execute_query(query, params)

        # Возвращаем массив (список) JSON
        return result

    def oneSelectBD(self, table, where_data):
        """
        Выполняет SELECT-запрос для получения одной строки по нескольким условиям.
        :param table: Название таблицы.
        :param where_data: Словарь с условиями для фильтрации (ключ - название колонки, значение - значение для сравнения).
        :return: Словарь с данными одной строки, соответствующей условиям, или None, если строка не найдена.
        """
        # Формируем условия WHERE
        where_clauses = [f"{column} = %s" for column in where_data.keys()]
        where_clause = " AND ".join(where_clauses)

        # Формируем SQL-запрос
        query = f"SELECT * FROM {table} WHERE {where_clause};"

        # Выполняем запрос с передачей параметров
        result, columns = self.execute_query(query, list(where_data.values()))

        # Если результат не пустой, возвращаем первую строку в виде словаря
        if result:
            return result[0]  # Возвращаем первую строку

        # Если строка не найдена, возвращаем None
        return None

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
