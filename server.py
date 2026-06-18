import sqlite3
from flask import Flask, jsonify, request, redirect, render_template

from Parcer_final import update_db_from_internet

# Создание веб приложения
app = Flask(__name__)

# Говорим серверу: если пользователь зайдет на главную страницу (просто слэш / ), запусти эту функцию
@app.route("/")
def home(): 
    connection = sqlite3.connect("quotes.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qutes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT,
        text TEXT
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM quotes")
    total_quotes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT author) FROM quotes")
    total_authors = cursor.fetchone()[0]

    stats_dict = {
        "total": total_quotes,
        "authors": total_authors
    }
    

    #Залезаем в базу данных

    cursor.execute("SELECT * FROM quotes")
    rows = cursor.fetchall()
    connection.close()

    #упаковываем данные в вид словоря
    quotes_list = []
    for row in rows:
        quotes_list.append({
            "id": row[0],
            "author": row[1],
            "text": row[2]
        })
    #Передаем этот список в html шаблон под именем 'quotes'
    return render_template("index.html", quotes=quotes_list, stats=stats_dict)

# МАРШРУТ ПАРСЕРА И ЗАПУСК
@app.route("/run_parser", methods=["POST"])
def run_parser():
    print("Пользователь нажал кнопку. Вызов парсера")

    #Вызов функции из соседнего файла 
    update_db_from_internet()

    return redirect("/")

# НОВЫЙ МАРШРУТ ДЛЯ ПРИЕМА ДАННЫХ (POST) ---
# Указываем что роут умеет слушать только post-запросы
@app.route("/add_quote", methods=["POST"])
def add_quote():
    #Вытаскиваем данные которые пользователь в вел поатрибуту name
    user_author = request.form.get("author_name")
    user_text = request.form.get("quote_text")

    #подключаемся к базе и вставляем новую строку
    connection = sqlite3.connect("quotes.db")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO quotes (author, text) VALUES (?, ?)",
        (user_author, user_text)
    )
    connection.commit()
    connection.close()

    #возврат обратно на главную
    return redirect("/")

# Если пользователь перейдет по /api/quotes/, запустится код
@app.route("/api/quotes")
def get_api_quotes():
    # подключаемся к нашей созданной базе SQL
    connection = sqlite3.connect("quotes.db")
    cursor = connection.cursor()

    # Достаем все строки из таблицы 
    cursor.execute("SELECT * FROM quotes")
    rows = cursor.fetchall()
    connection.close()
    #Возвращаем в формат JSON
    return jsonify([{"id": r[0], "author": r[1], "text": r[2]} for r in rows])

# способ удаления цитаты
# <int:quote_id> означает что в URL прилетит число например:(/delete_quote/5)
@app.route("/delete_quote/<int:quote_id>")
def delete_quote(quote_id):
    #Подключение к базе
    connection = sqlite3.connect("quotes.db")
    cursor = connection.cursor()

    #выполняем SQL команду удаления по конкретному ид
    cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))

    connection.commit()
    connection.close()

    print(f"[СИСТЕМА]: Цитата с ID {quote_id} успешно удалена.")

    return redirect("/")

#запускаем веб сервер, если файл запущен на прямую
if __name__ == "__main__":
    app.run(debug=True)