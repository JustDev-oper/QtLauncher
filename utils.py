import json

from db import get_data_path


class TXTEditor:
    def __init__(self):
        self.path = get_data_path() / "last_games.txt"

    def create_txt(self):
        if not self.path.exists():
            with open(self.path, "w", encoding="utf-8") as file:
                pass

    def get_last_games(self):
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                file_data = file.read()
                return file_data.split("\n")
        except FileNotFoundError:
            return []

    def add_game_to_history(self, game_name):
        current_games = self.get_last_games()
        current_games = [
            game for game in current_games if
            game != game_name and game.strip()
        ]
        current_games.insert(0, game_name)
        current_games = current_games[:5]
        self.save_last_games(current_games)

    def save_last_games(self, games_list):
        with open(self.path, "w", encoding="utf-8") as file:
            for game in games_list:
                if game.strip():
                    file.write(game + "\n")

    def clear_game_history(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("")


class JSONEditor:
    def __init__(self):
        self.path = get_data_path() / "settings.json"

    def create_json(self):
        if not self.path.exists():
            default_settings = {"theme": "dark"}
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(default_settings, file, indent=4, ensure_ascii=False)

    def get_theme(self):
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                settings = json.load(file)
                return settings.get("theme", "dark")
        except (FileNotFoundError, json.JSONDecodeError):
            return "dark"

    def update_setting(self, key, value):
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings[key] = value

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)


txt_editor = TXTEditor()
json_editor = JSONEditor()
