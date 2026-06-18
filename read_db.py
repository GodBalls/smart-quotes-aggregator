import sqlite3

#подключение к базе данных 
connection = sqlite3.connect("quotes.db")
cursor = connection.cursor()

# Пишем SQL запрос выбрать все это * из таблицы
cursor.execute("SELECT * FROM quotes")

#забираем все найденные строчки из курсора в переменную rows
# Метод .fetchall() выкачивает все запросы в виде списка 
rows = cursor.fetchall()

print("ДОСТАЕМ ДАННЫЕ ИЗ БАЗЫ")

# Перебераем циклом все полученные данные 
for row in rows:
    #База данных возвращает каждую строку в виде кортежа(id, author, text)
    # Индекс 0 - это id, 1 - author,  - text.
    print(f"ID: {row[0]}, Автор: {row[1]}") 
    print(f"Цитата: {row[2]}")
    print("-" * 50)

# Закрываем соединение
connection.close()