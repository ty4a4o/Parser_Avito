import sqlite3

db = sqlite3.connect('Avito_db.db')

cur = db.cursor() # Создать курсор

# Добавление таблиц
# cur.execute("CREATE TABLE orders (
#     orders_name text,
#     orders_URL text,
#     orders_price integer
# )")

# Удалить таблицу
# cur.execute("DROP TABLE users")

# Удалить записи
# cur.execute("DELETE FROM users WHERE rowid = 2")

#  Добавление данных
# cur.execute("INSERT INTO users VALUES ('Бондаренко Михаил Петрович', '89191234567', 'bondar@mail.ru', '123', '', '100')")

# Изменение данных
# cur.execute("UPDATE users SET")

# Выбор данных
cur.execute("SELECT rowid, * FROM users")
# item = cur.fetchall() # Для точечного вывода
print(cur.fetchall()) # Все записи
# print(cur.fetchmany(1)) # Вывод 1 записи (список)
# print(cur.fetchone()[1]) # Вывод 1 записи (кортеж)

# for elem in item:
#     print(elem[1] + "\n" + elem[4])

db.commit() # Обновление БД
db.close()