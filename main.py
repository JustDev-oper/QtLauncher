import os
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

import dialogs
from db import database
from ui.mainWindow_ui import Ui_MainWindow
from utils import txt_editor, json_editor


def resource_path(relative_path: str) -> str:
    """Корректный путь к файлу для работы из .py и из .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class QtLauncher(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(750, 420)
        self.setupUi(self)

        self.update_game_list()
        txt_editor.create_txt()
        self.update_last_game_list()
        json_editor.create_json()

        theme_file = resource_path(f"style/{json_editor.get_theme()}.qss")
        with open(theme_file, "r", encoding="utf-8") as qss:
            self.setStyleSheet(qss.read())

        # Сигналы
        self.add_game.clicked.connect(self.open_dialog)
        self.list_games.itemDoubleClicked.connect(self.open_game)
        self.delete_game.clicked.connect(self.delete_game_from_list)
        self.sort_name_a_z.clicked.connect(lambda: self.sort_games(""))
        self.sort_name_z_a.clicked.connect(lambda: self.sort_games("r"))
        self.action_2.triggered.connect(lambda: self.set_theme("light"))
        self.action_3.triggered.connect(lambda: self.set_theme("dark"))

    def set_theme(self, theme):
        theme_file = resource_path(f"style/{theme}.qss")
        with open(theme_file, "r", encoding="utf-8") as qss:
            self.setStyleSheet(qss.read())
        json_editor.update_setting("theme", theme)

    def update_game_list(self):
        games = database.get_games()
        self.list_games.clear()
        for game in games:
            self.list_games.addItem(game)

    def update_last_game_list(self):
        games = txt_editor.get_last_games()
        self.last_games.clear()
        for game in games:
            self.last_games.addItem(game)

    def sort_games(self, mode):
        games = database.get_games()
        sorted_games = sorted(games, reverse=(mode == "r"))
        self.list_games.clear()
        for game in sorted_games:
            self.list_games.addItem(game)

    def delete_game_from_list(self):
        current_item = self.list_games.currentItem()
        if current_item:
            game_name = current_item.text()
            database.delete_game(game_name)
            current_row = self.list_games.currentRow()
            self.list_games.takeItem(current_row)
            self.list_games.clearSelection()

    def open_game(self, item):
        game = database.get_game(item.text())
        try:
            txt_editor.add_game_to_history(game[1])
            os.startfile(game[2])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка!", str(e))
        self.update_last_game_list()

    def open_dialog(self):
        dialog = dialogs.AddGameDialog()
        dialog.exec()
        self.update_game_list()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wind = QtLauncher()
    wind.show()
    sys.exit(app.exec())
