import os
import sys

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

import dialogs
from db import database
from ui.mainWindow import Ui_MainWindow
from utils import txt_editor, json_editor


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class QtLauncher(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(750, 400)
        self.setupUi(self)

        self.update_game_list()
        txt_editor.create_txt()
        self.update_last_game_list()
        json_editor.create_json()

        self.update_menu_bar()

        database.check_category_id_is_valid()

        theme_file = resource_path(f"style/{json_editor.get_theme()}.qss")
        with open(theme_file, "r", encoding="utf-8") as qss:
            self.setStyleSheet(qss.read())

        # Сигналы
        self.add_game.clicked.connect(lambda: self.open_dialog("add_game"))
        self.list_games.itemDoubleClicked.connect(self.open_game)
        self.delete_game.clicked.connect(self.delete_game_from_list)
        self.sort_name_a_z.clicked.connect(lambda: self.sort_games(""))
        self.sort_name_z_a.clicked.connect(lambda: self.sort_games("r"))
        self.action_2.triggered.connect(lambda: self.set_theme("light"))
        self.action_3.triggered.connect(lambda: self.set_theme("dark"))
        self.create_category.triggered.connect(
            lambda: self.open_dialog("add_category"))
        self.delete_category.triggered.connect(
            lambda: self.open_dialog("delete_category")
        )
        self.edit_game.clicked.connect(lambda: self.open_dialog("edit_game"))

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
        items = []
        for i in range(self.list_games.count()):
            items.append(self.list_games.item(i).text())

        sorted_items = sorted(items, reverse=(mode == "r"))

        self.list_games.clear()
        for game_name in sorted_items:
            self.list_games.addItem(game_name)

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

    def open_dialog(self, dialog):
        if dialog == "add_game":
            _dialog = dialogs.AddGameDialog()
            _dialog.exec()
            self.update_game_list()
        if dialog == "add_category":
            _dialog = dialogs.AddCategoryDialog()
            _dialog.exec()
            self.update_menu_bar()
        if dialog == "delete_category":
            _dialog = dialogs.DeleteCategoryDialog()
            _dialog.exec()
            self.update_menu_bar()
        if dialog == "edit_game":
            current_item = self.list_games.currentItem()
            if current_item:
                game_name = current_item.text()
                _dialog = dialogs.EditGameDialog(game_name)
                _dialog.exec()
                self.update_game_list()

    def update_menu_bar(self):
        menu = self.menu_3
        actions = menu.actions()

        separator_index = -1
        for i, action in enumerate(actions):
            if action.isSeparator():
                separator_index = i
                break

        if separator_index != -1:
            for action in actions[separator_index + 1:]:
                menu.removeAction(action)

        categories = database.get_categories()
        for category in categories:
            category_name = category[0]
            action = QAction(category_name, self)
            action.triggered.connect(
                lambda checked,
                       cat_name=category_name: self.on_category_selected(
                    cat_name
                )
            )
            menu.addAction(action)

    def on_category_selected(self, category_name):
        self.filter_games_by_category(category_name)

    def filter_games_by_category(self, category_name):
        if category_name != "Все":
            category_id = database.get_category_id_by_name(category_name)

            if category_id:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM Games WHERE category_id = ?",
                    (category_id,),
                )
                games = cursor.fetchall()
                conn.close()

                self.list_games.clear()
                for game in games:
                    self.list_games.addItem(game[0])
            else:
                self.update_game_list()
        else:
            self.list_games.clear()
            self.update_game_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wind = QtLauncher()
    wind.show()
    sys.exit(app.exec())
