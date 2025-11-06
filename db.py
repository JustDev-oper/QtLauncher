import hashlib
import sqlite3

from utils import get_data_path


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UserManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._current_user_id = None
        self._current_user_login = None
        self._load_session()

    def register_user(self, login: str, password: str) -> bool:

        if self.user_exists(login):
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO Users (login, password) VALUES (?, ?)",
                (login, hashed_password),
            )
            user_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO Categories (name, user_id) VALUES (?, ?)",
                ("Все", user_id),
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при регистрации пользователя: {e}")
            return False
        finally:
            conn.close()

    def login_user(self, login: str, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)
            cursor.execute(
                "SELECT id, login FROM Users WHERE login = ? AND password = ?",
                (login, hashed_password),
            )
            user = cursor.fetchone()
            if user:
                self._current_user_id = user[0]
                self._current_user_login = user[1]
                self._save_session()
                from utils import data_manager
                data_manager.update_current_user(self._current_user_id)
                return True
            return False
        finally:
            conn.close()

    def user_exists(self, login: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM Users WHERE login = ?", (login,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()

    def get_current_user_id(self) -> int | None:
        if not self._current_user_id:
            self._load_session()
        return self._current_user_id

    def get_current_user_login(self) -> str | None:
        if not self._current_user_login:
            self._load_session()
        return self._current_user_login

    def is_authenticated(self) -> bool:
        return bool(self.get_current_user_id())

    def logout(self):
        self._current_user_id = None
        self._current_user_login = None
        self._delete_session()
        from utils import data_manager
        data_manager.update_current_user(None)

    def _save_session(self):
        from utils import data_manager

        if (
            self._current_user_id is not None
            and self._current_user_login is not None
        ):
            data_manager.session.save_session(
                self._current_user_id, self._current_user_login
            )
        else:
            data_manager.session.clear_session()

    def _load_session(self):
        from utils import data_manager

        self._current_user_id, self._current_user_login = (
            data_manager.session.load_session()
        )

    def _delete_session(self):
        from utils import data_manager

        data_manager.session.clear_session()


class Database:
    def __init__(self):
        self.data_path = get_data_path()
        self.db_path = self.data_path / "games.db"
        self.users = UserManager(self.db_path)
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE(name, user_id),
            FOREIGN KEY (user_id) REFERENCES Users (id)
            )"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL UNIQUE,
            category_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES Categories(id),
            FOREIGN KEY (user_id) REFERENCES Users(id)
            )"""
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
            )"""
        )

        conn.commit()
        conn.close()

    def check_unique(self, select_from, where_value, parameter):
        conn = self.get_connection()
        cursor = conn.cursor()
        if select_from in ["Games", "Categories"]:
            user_id = self.users.get_current_user_id()
            cursor.execute(
                f"SELECT COUNT(*) FROM {select_from} WHERE {where_value} = ? AND user_id = ?",
                (parameter, user_id),
            )
        else:
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
            user_id = self.users.get_current_user_id()
            cursor.execute(
                "INSERT INTO Games (name, path, category_id, user_id) VALUES (?, ?, ?, ?)",
                (name, game_path, category_id, user_id),
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
            user_id = self.users.get_current_user_id()

            cursor.execute(
                "SELECT COUNT(*) FROM Categories WHERE name = ? AND user_id = ?",
                (name, user_id),
            )
            if cursor.fetchone()[0] > 0:
                return False

            cursor.execute(
                "INSERT INTO Categories (name, user_id) VALUES (?, ?)",
                (name, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении категории: {e}")
            return False
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
        user_id = self.users.get_current_user_id()
        cursor.execute(
            "SELECT * FROM Games WHERE category_id = ? AND user_id = ?",
            (category_id, user_id),
        )
        games = cursor.fetchall()
        conn.close()
        return games

    def edit_games_category(self, category_id_old, category_id_new):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            user_id = self.users.get_current_user_id()
            cursor.execute(
                "UPDATE Games SET category_id = ? WHERE category_id = ? AND user_id = ?",
                (category_id_new, category_id_old, user_id),
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
            user_id = self.users.get_current_user_id()
            cursor.execute(
                "SELECT id FROM Categories WHERE user_id = ?", (user_id,)
            )
            valid_category_ids = {row[0] for row in cursor.fetchall()}

            if not valid_category_ids:
                return

            cursor.execute(
                "SELECT id, name, category_id FROM Games WHERE category_id NOT IN ({}) AND user_id = ?".format(
                    ",".join("?" for _ in valid_category_ids)
                ),
                list(valid_category_ids) + [user_id],
            )

            invalid_games = cursor.fetchall()

            for game_id, game_name, old_category_id in invalid_games:
                cursor.execute(
                    "UPDATE Games SET category_id = ? WHERE id = ? AND user_id = ?",
                    (1, game_id, user_id),
                )

            conn.commit()
        except Exception as e:
            print(f"Ошибка при проверке категорий: {e}")
        finally:
            conn.close()

    def get_categories(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        user_id = self.users.get_current_user_id()
        cursor.execute(
            """SELECT name FROM Categories 
            WHERE user_id = ?
            ORDER BY CASE name WHEN 'Все' THEN 0 ELSE 1 END, name""",
            (user_id,),
        )
        categories = cursor.fetchall()
        conn.close()
        return categories

    def get_category_name_by_id(self, _id):
        conn = self.get_connection()
        cursor = conn.cursor()
        user_id = self.users.get_current_user_id()
        cursor.execute(
            "SELECT name FROM Categories WHERE id = ? AND user_id = ?",
            (_id, user_id),
        )
        name = cursor.fetchone()[0]
        conn.close()
        return name

    def get_category_id_by_name(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        user_id = self.users.get_current_user_id()
        cursor.execute(
            "SELECT id FROM Categories WHERE name = ? AND user_id = ?",
            (name, user_id),
        )
        result = cursor.fetchone()
        _id = result[0] if result else None
        conn.close()
        return _id

    def get_games(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        user_id = self.users.get_current_user_id()
        cursor.execute("SELECT name FROM Games WHERE user_id = ?", (user_id,))
        games = cursor.fetchall()
        conn.close()

        game_names = [game[0] for game in games]
        return game_names

    def get_game(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        user_id = self.users.get_current_user_id()
        cursor.execute(
            "SELECT * FROM Games WHERE name = ? AND user_id = ?",
            (name, user_id),
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def update_game(self, old_name, new_name, category_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            user_id = self.users.get_current_user_id()
            cursor.execute(
                "UPDATE Games SET name = ?, category_id = ? WHERE name = ? AND user_id = ?",
                (new_name, category_id, old_name, user_id),
            )
            conn.commit()
        except Exception as e:
            print(str(e))
        finally:
            conn.close()


database = Database()
