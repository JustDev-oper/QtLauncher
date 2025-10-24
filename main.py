import os
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

import dialogs
from db import database
from ui.mainWindow_ui import Ui_MainWindow
from utils import create_json, get_theme, update_setting, add_game_to_history, \
    get_last_games, create_txt


class QtLauncher(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(750, 420)

        self.setupUi(self)
        self.update_game_list()

        create_txt()
        self.update_last_game_list()

        create_json()

        with open(f'style/{get_theme()}.qss') as qss:
            self.setStyleSheet(qss.read())

        self.add_game.clicked.connect(self.open_dialog)
        self.list_games.itemDoubleClicked.connect(self.open_game)
        self.delete_game.clicked.connect(self.delete_game_from_list)

        self.sort_name_a_z.clicked.connect(lambda: self.sort_games(""))
        self.sort_name_z_a.clicked.connect(lambda: self.sort_games("r"))

        self.action_2.triggered.connect(lambda: self.set_theme("light"))
        self.action_3.triggered.connect(lambda: self.set_theme("dark"))

    def set_theme(self, theme):
        with open(f'style/{theme}.qss') as qss:
            self.setStyleSheet(qss.read())
        update_setting("theme", theme)

    def update_game_list(self):
        games = database.get_games()
        self.list_games.clear()
        for game in games:
            self.list_games.addItem(game)

    def update_last_game_list(self):
        games = get_last_games()
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
            add_game_to_history(game[1])
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
