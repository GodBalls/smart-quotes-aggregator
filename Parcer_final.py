import sqlite3
import requests
from bs4 import BeautifulSoup

def update_db_from_internet():
    print("НАЧИНАЮ ФОНОВОЕ СКАЧИВАНИЕ ЦИТАТ")

    # маскировка под браузер
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate", 
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
        }

    url = "https://quotes.toscrape.com/"

    try:
        # Скачиваем страницу передавая маскировку под браузер
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("[УСПЕХ]: код страницы получен. начинаем разбор")

            #Передаем живой html в BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Находим все блоки с цитататами на странице и получаем список
            all_quote = soup.find_all("div", class_="quote")
        
                #Подключаемся к файлу базы данных если его нет пайтон сам создаст его 
            connection = sqlite3.connect("quotes.db")

            # Создаем курсор это наш рабочий инструмент. Через него мы отправляем команды в базу SQL
            cursor = connection.cursor()

            # Ниже запрос на создание таблицы в SQL
            # Первой строкой мы создаем базу данных quotes
            # дальше мы создаем первую колонку у каждой цитаты будет свой номер и все автоматически будет простовлять нумерацию (в краце)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT,
                text TEXT
            )
            """)

            counter = 0
            for block in all_quote:
                #внутри текущего блока ищем текст цитаты 
                text = block.find("span", class_="text").text
                # Внутри этого же блока ищем автора 
                author = block.find("small", class_="author").text

                #защита от дублей
                cursor.execute("SELECT id FROM quotes WHERE text = ?", (text,))
                if not cursor.fetchone():
            
                    # Вместо записи в файл кидаем SQL команду вставки:
                    cursor.execute(
                        "INSERT INTO quotes(author, text) VALUES(?, ?)",
                        (author, text)
                    )
                    counter += 1

            # Сохранение изменений в файле базы знаний
            connection.commit()

            # Закрываем соединение 
            connection.close()

            print(f"Добавленно новых цитат: {counter}")
            return True
        else:
            print(f"САЙТ ВЕРНУЛ СТАТУС: {response.status_code}")
            return False
    except Exception as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА]: что-то пошло не так: {e}")
        return False

