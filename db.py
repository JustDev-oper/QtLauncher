import os
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
            """CREATE TABLE IF NOT EXISTS Games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL UNIQUE
            )"""
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

    def insert_game(self, name, game_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Games (name, path) VALUES (?, ?)",
                (name, game_path),
            )
            conn.commit()
            print(f"Игра '{name}' добавлена в базу данных")
        except sqlite3.IntegrityError:
            print(f"Ошибка: игра с именем '{name}' уже существует")
        except Exception as e:
            print(f"Ошибка при добавлении игры: {e}")
        finally:
            conn.close()

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
