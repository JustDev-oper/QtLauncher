import sqlite3

from utils import get_data_path


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

    def check_unique(self, select_from, where_value, parameter):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM {select_from} WHERE {where_value} = ?",
            (parameter,),
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
        except Exception as e:
            print(f"Ошибка при добавлении категории: {e}")
        finally:
            conn.close()

    def delete(self, select_from, where_value, parameter):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"DELETE FROM {select_from} WHERE {where_value} = ?",
                (parameter,),
            )
            conn.commit()
        except Exception as e:
            print(f"Ошибка при удалении: {e}")
        finally:
            conn.close()

    def get_games_by_category(self, category_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Games WHERE category_id = ?", (category_id,)
        )
        games = cursor.fetchall()
        conn.close()
        return games

    def edit_games_category(self, category_id_old, category_id_new):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Games SET category_id = ? WHERE category_id = ?",
                (category_id_new, category_id_old),
            )
            conn.commit()
        except Exception as e:
            print(f"Ошибка при изменении категории для игры: {str(e)}")
        finally:
            conn.close()

    def check_category_id_is_valid(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM Categories")
            valid_category_ids = {row[0] for row in cursor.fetchall()}

            cursor.execute(
                "SELECT id, name, category_id FROM Games WHERE category_id NOT IN ({})".format(
                    ",".join("?" for _ in valid_category_ids)
                ),
                list(valid_category_ids),
            )

            invalid_games = cursor.fetchall()

            for game_id, game_name, old_category_id in invalid_games:
                cursor.execute(
                    "UPDATE Games SET category_id = ? WHERE id = ?",
                    (1, game_id),
                )

            conn.commit()
        except Exception as e:
            print(f"Ошибка при проверке категорий: {e}")
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

    def update_game(self, old_name, new_name, category_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Games SET name = ?, category_id = ? WHERE name = ?",
                (new_name, category_id, old_name),
            )
            conn.commit()
        except Exception as e:
            print(str(e))

        finally:
            conn.close()


database = Database()
