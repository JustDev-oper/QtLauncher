import json

from db import get_data_path

PATH_JSON = get_data_path() / "settings.json"
PATH_LAST_GAME = get_data_path() / "last_games.txt"


def create_json():
    if not PATH_JSON.exists():
        default_settings = {
            "theme": "dark"
        }
        with open(PATH_JSON, 'w', encoding='utf-8') as file:
            json.dump(default_settings, file, indent=4, ensure_ascii=False)


def create_txt():
    if not PATH_LAST_GAME.exists():
        with open(PATH_LAST_GAME, 'w', encoding='utf-8') as file:
            file.write('')


def get_theme():
    try:
        with open(PATH_JSON, 'r', encoding='utf-8') as file:
            settings = json.load(file)
            return settings.get("theme",
                                "dark")
    except (FileNotFoundError, json.JSONDecodeError):
        return "dark"


def get_last_games():
    try:
        with open(PATH_LAST_GAME, 'r', encoding='utf-8') as file:
            file_data = file.read()
            return file_data.split("\n")
    except FileNotFoundError:
        return []


def update_setting(key, value):
    try:
        with open(PATH_JSON, 'r', encoding='utf-8') as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    settings[key] = value

    with open(PATH_JSON, 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)


def add_game_to_history(game_name):
    current_games = get_last_games()
    current_games = [game for game in current_games if
                     game != game_name and game.strip()]
    current_games.insert(0, game_name)
    current_games = current_games[:5]
    save_last_games(current_games)


def save_last_games(games_list):
    with open(PATH_LAST_GAME, 'w', encoding='utf-8') as file:
        for game in games_list:
            if game.strip():
                file.write(game + '\n')


def clear_game_history():
    with open(PATH_LAST_GAME, 'w', encoding='utf-8') as file:
        file.write('')
