import sqlite3
from pathlib import Path


def get_data_path():
    documents_path = Path.home() / "Documents"
    data_path = documents_path / "QtLauncher_Data"
    data_path.mkdir(exist_ok=True)
    return data_path


class Database:
    def __init__(self):
        self.data_path = get_data_path()
        self.db_path = self.data_path / "games.db"
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL UNIQUE,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES Categories(id)
            )"""
        )

        cursor.execute(
            "INSERT OR IGNORE INTO Categories (name) VALUES (?)", ("Все",)
        )

        conn.commit()
        conn.close()

    def check_name_is_unique(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Games WHERE name = ?", (name,))
        count = cursor.fetchone()[0]
        return count == 0

    def check_path_is_unique(self, game_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Games WHERE path = ?", (game_path,)
        )
        count = cursor.fetchone()[0]
        return count == 0

    def insert_game(self, name, game_path, category_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Games (name, path, category_id) VALUES (?, ?, ?)",
                (name, game_path, category_id),
            )
            conn.commit()
            print(f"Игра '{name}' добавлена в базу данных")
        except sqlite3.IntegrityError:
            print(f"Ошибка: игра с именем '{name}' уже существует")
        except Exception as e:
            print(f"Ошибка при добавлении игры: {e}")
        finally:
            conn.close()

    def insert_category(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Categories (name) VALUES (?)",
                (name,),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Ошибка: категория с именем '{name}' уже существует")
        except Exception as e:
            print(f"Ошибка при добавлении категории: {e}")
        finally:
            conn.close()

    def get_categories(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT name FROM Categories""")
        categories = cursor.fetchall()
        conn.close()
        return categories

    def get_category_name_by_id(self, _id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Categories WHERE id = ?", (_id,))
        name = cursor.fetchone()[0]
        conn.close()
        return name

    def get_category_id_by_name(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Categories WHERE name = ?", (name,))
        _id = cursor.fetchone()[0]
        conn.close()
        return _id

    def category_name_check_unique(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Categories WHERE name = ?", (name,)
        )
        count = cursor.fetchone()[0]
        return count == 0

    def delete_game(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Games WHERE name = ?", (name,))
        conn.commit()
        conn.close()

    def get_games(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Games")
        games = cursor.fetchall()
        conn.close()

        game_names = [game[0] for game in games]
        return game_names

    def get_game(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Games WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        return row


database = Database()
