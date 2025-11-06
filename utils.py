import json
from pathlib import Path


def get_data_path():
    documents_path = Path.home() / "Documents"
    data_path = documents_path / "QtLauncher_Data"
    data_path.mkdir(exist_ok=True)
    return data_path


class FileManager:
    def __init__(self, filename):
        self.path = get_data_path() / filename

    def ensure_exists(self, default_content=None):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if default_content is not None:
                self._write_content(default_content)
            else:
                self.path.touch()

    def _read_content(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return file.read()

    def _write_content(self, content):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(content)


class SessionManager:
    def __init__(self):
        self.file_manager = FileManager("session.json")
        self.file_manager.ensure_exists("{}")

    def save_session(self, user_id: int, login: str):
        import json

        session_data = {"user_id": user_id, "login": login}
        self.file_manager._write_content(json.dumps(session_data))

    def load_session(self) -> tuple[int | None, str | None]:
        import json

        try:
            content = self.file_manager._read_content()
            session_data = json.loads(content)
            return session_data.get("user_id"), session_data.get("login")
        except (FileNotFoundError, json.JSONDecodeError):
            return None, None

    def clear_session(self):
        import os

        try:
            os.remove(self.file_manager.path)
        except FileNotFoundError:
            pass


class GameHistoryManager:
    def __init__(self):
        self.file_manager = FileManager("last_games.txt")
        self.file_manager.ensure_exists()

    def get_last_games(self):
        try:
            content = self.file_manager._read_content()
            return [game for game in content.split("\n") if game.strip()]
        except FileNotFoundError:
            return []

    def add_game(self, game_name):
        games = self.get_last_games()
        # Удаляем дубликат и добавляем в начало
        games = [game for game in games if game != game_name]
        games.insert(0, game_name)
        # Ограничиваем историю 5 играми
        games = games[:5]
        self._save_games(games)

    def _save_games(self, games):
        content = "\n".join(game for game in games if game.strip())
        self.file_manager._write_content(content)

    def clear_history(self):
        self.file_manager._write_content("")


class SettingsManager:
    def __init__(self):
        self.file_manager = FileManager("settings.json")
        self.file_manager.ensure_exists('{"theme": "dark"}')

    def get_setting(self, key, default=None):
        try:
            content = self.file_manager._read_content()
            settings = json.loads(content)
            return settings.get(key, default)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def update_setting(self, key, value):
        try:
            content = self.file_manager._read_content()
            settings = json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings[key] = value
        self.file_manager._write_content(
            json.dumps(settings, indent=4, ensure_ascii=False)
        )


class DataManager:
    def __init__(self):
        self.history = GameHistoryManager()
        self.settings = SettingsManager()
        self.session = SessionManager()

    def get_last_games(self):
        return self.history.get_last_games()

    def add_game_to_history(self, game_name):
        self.history.add_game(game_name)

    def clear_game_history(self):
        self.history.clear_history()

    def get_theme(self):
        return self.settings.get_setting("theme", "dark")

    def set_theme(self, theme):
        self.settings.update_setting("theme", theme)

    def update_setting(self, key, value):
        self.settings.update_setting(key, value)


data_manager = DataManager()
