import os
import sys

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QMenu

import dialogs
from db import database
from ui.mainWindow import Ui_MainWindow
from utils import data_manager


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class QtLauncher(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(750, 400)
        self.setupUi(self)

        self.profile_menu = QMenu(self)

        self.switch_user_action = QAction("Сменить пользователя", self)
        self.switch_user_action.triggered.connect(self.switch_user)
        self.profile_menu.addAction(self.switch_user_action)

        self.profile_menu.addSeparator()

        self.logout_action = QAction("Выйти", self)
        self.logout_action.triggered.connect(self.logout)
        self.profile_menu.addAction(self.logout_action)

        self.profile_action = QAction("Профиль", self)
        self.profile_action.triggered.connect(
            lambda: self.open_dialog("profile")
        )
        self.profile_action.setMenu(self.profile_menu)
        self.menuBar.addAction(self.profile_action)

        if not database.users.is_authenticated():
            if not self.show_auth_dialog():
                return
        else:
            self.update_profile_button()

        self.update_game_list()
        self.update_last_game_list()
        self.update_menu_bar()
        database.check_category_id_is_valid()

        theme_file = resource_path(f"style/{data_manager.get_theme()}.qss")
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
            lambda: self.open_dialog("add_category")
        )
        self.delete_category.triggered.connect(
            lambda: self.open_dialog("delete_category")
        )
        self.edit_game.clicked.connect(lambda: self.open_dialog("edit_game"))

    def set_theme(self, theme):
        theme_file = resource_path(f"style/{theme}.qss")
        with open(theme_file, "r", encoding="utf-8") as qss:
            self.setStyleSheet(qss.read())
        data_manager.update_setting("theme", theme)

    def update_game_list(self):
        games = database.get_games()
        self.list_games.clear()
        for game in games:
            self.list_games.addItem(game)

    def update_last_game_list(self):
        games = data_manager.get_last_games()
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
            database.delete(
                select_from="Games", where_value="name", parameter=game_name
            )
            current_row = self.list_games.currentRow()
            self.list_games.takeItem(current_row)
            self.list_games.clearSelection()

    def open_game(self, item):
        game = database.get_game(item.text())
        try:
            data_manager.add_game_to_history(game[1])
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
            self.update_game_list()
            self.update_menu_bar()
        if dialog == "edit_game":
            current_item = self.list_games.currentItem()
            if current_item:
                game_name = current_item.text()
                _dialog = dialogs.EditGameDialog(game_name)
                _dialog.exec()
                self.update_game_list()
        if dialog == "profile":
            if not database.users.is_authenticated():
                self.show_auth_dialog()
            else:
                QMessageBox.information(
                    self,
                    "Профиль",
                    f"Вы вошли как: {database.users.get_current_user_login()}",
                )

    def show_auth_dialog(self):
        _dialog = dialogs.ProfileDialog()
        result = _dialog.exec()

        if not result or not _dialog.login_success:
            self.close()
            return False

        self.update_profile_button()
        return True

    def update_profile_button(self):
        if database.users.is_authenticated():
            self.profile_action.setText(
                f"Профиль ({database.users.get_current_user_login()})"
            )
        else:
            self.profile_action.setText("Войти")

    def reload_user_data(self):
        self.update_profile_button()
        self.list_games.clear()
        self.last_games.clear()
        self.update_game_list()
        self.update_last_game_list()
        self.update_menu_bar()
        database.check_category_id_is_valid()

    def switch_user(self):
        database.users.logout()
        if self.show_auth_dialog():
            self.reload_user_data()
        else:
            # Если пользователь отменил вход, выходим из приложения
            self.close()

    def logout(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы хотите выйти из системы или сменить пользователя?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

        if reply == QMessageBox.StandardButton.Yes:  # Выйти
            database.users.logout()
            self.close()
        elif reply == QMessageBox.StandardButton.No:  # Сменить пользователя
            self.switch_user()

        if reply == 0:  # Выйти
            database.users.logout()
            self.close()
        elif reply == 1:  # Сменить пользователя
            self.switch_user()

    def update_menu_bar(self):
        menu = self.menu_3
        actions = menu.actions()

        separator_index = -1
        for i, action in enumerate(actions):
            if action.isSeparator():
                separator_index = i
                break

        if separator_index != -1:
            for action in actions[separator_index + 1 :]:
                menu.removeAction(action)

        categories = database.get_categories()
        for category in categories:
            category_name = category[0]
            action = QAction(category_name, self)
            action.triggered.connect(
                lambda checked, cat_name=category_name: self.on_category_selected(
                    cat_name
                )
            )
            menu.addAction(action)

    def on_category_selected(self, category_name):
        self.filter_games_by_category(category_name)

    def filter_games_by_category(self, category_name):
        if not database.users.is_authenticated():
            return

        self.list_games.clear()

        if category_name == "Все":
            # Показываем все игры пользователя
            self.update_game_list()
            return

        category_id = database.get_category_id_by_name(category_name)
        if category_id:
            # Показываем игры только из выбранной категории
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM Games WHERE category_id = ? AND user_id = ?",
                (category_id, database.users.get_current_user_id()),
            )
            games = cursor.fetchall()
            conn.close()

            for game in games:
                self.list_games.addItem(game[0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wind = QtLauncher()
    wind.show()
    sys.exit(app.exec())
