from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox

from db import database
from ui.add_game_dialog import Ui_Dialog as AddGameUI
from ui.createCategory import Ui_Dialog as AddCategoryUI
from ui.deleteCategory import Ui_Dialog as DeleteCategoryUI
from ui.edit_game_dialog_ui import Ui_Dialog as EditGameUI


class AddGameDialog(QDialog, AddGameUI):
    def __init__(self):
        super().__init__()
        self.setFixedSize(450, 180)

        self.setupUi(self)
        self.path_button.clicked.connect(self.choose_file)

        self.buttonBox.accepted.disconnect()
        self.buttonBox.rejected.disconnect()

        self.get_categories()

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

    def get_categories(self):
        combobox = self.comboBox
        categories = database.get_categories()
        for category in categories:
            combobox.addItem(category[0])

    def choose_file(self):
        file_path = QFileDialog.getOpenFileName(
            self, "Выбрать файл", "", "EXE - Файл (*.exe)"
        )[0]
        if file_path:
            self.file_path.setText(file_path)

    def accept_dialog(self):
        game_name = self.game_name.text().strip()
        game_path = self.file_path.text().strip()
        category_id = database.get_category_id_by_name(
            self.comboBox.currentText())

        if not game_name:
            QMessageBox.warning(self, "Ошибка", "Введите название игры")
            return

        if not game_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл игры")
            return

        if not category_id:
            category_id = 1

        if not database.check_name_is_unique(game_name):
            QMessageBox.warning(self, "Ошибка",
                                "Игра с таким именем уже существует")
            return

        if not database.check_path_is_unique(game_path):
            QMessageBox.warning(self, "Ошибка",
                                "Игра с таким путём уке существует")
            return

        try:
            database.insert_game(game_name, game_path, category_id)
            self.accept()
            QMessageBox.information(self, "Успех", "Игра добавлена!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось добавить игру: {str(e)}")


class EditGameDialog(QDialog, EditGameUI):
    def __init__(self, game_name):
        super().__init__()
        self.orig_game_name = game_name
        self.setFixedSize(450, 180)

        self.setupUi(self)

        self.buttonBox.accepted.disconnect()
        self.buttonBox.rejected.disconnect()

        self.get_categories()
        self.load_game_data()

        self.path_button.setDisabled(True)

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

    def get_categories(self):
        combobox = self.comboBox
        categories = database.get_categories()
        for category in categories:
            combobox.addItem(category[0])

    def load_game_data(self):
        game_data = database.get_game(self.orig_game_name)
        if game_data:
            self.game_name.setText(game_data[1])  # name
            self.file_path.setText(game_data[2])  # path

            # Устанавливаем правильную категорию
            category_name = database.get_category_name_by_id(game_data[3])
            index = self.comboBox.findText(category_name)
            if index >= 0:
                self.comboBox.setCurrentIndex(index)

    def accept_dialog(self):
        new_game_name = self.game_name.text().strip()
        category_id = database.get_category_id_by_name(
            self.comboBox.currentText())

        if not new_game_name:
            QMessageBox.warning(self, "Ошибка", "Введите название игры")
            return

        if not category_id:
            category_id = 1

        # Проверяем уникальность имени, только если имя изменилось
        if new_game_name != self.orig_game_name and not database.check_name_is_unique(
                new_game_name):
            QMessageBox.warning(self, "Ошибка",
                                "Игра с таким именем уже существует")
            return

        try:
            database.update_game(self.orig_game_name, new_game_name,
                                 category_id)
            self.accept()
            QMessageBox.information(self, "Успех", "Игра обновлена!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось обновить игру: {str(e)}")


class AddCategoryDialog(QDialog, AddCategoryUI):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 110)

        self.setupUi(self)

        self.buttonBox.accepted.disconnect()
        self.buttonBox.rejected.disconnect()

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

    def accept_dialog(self):
        category_name = self.lineEdit.text().strip()
        if not category_name:
            QMessageBox.warning(self, "Ошибка",
                                "Категория не может быть пустой")
            return

        if not database.category_name_check_unique(category_name):
            QMessageBox.warning(self, "Ошибка",
                                "Категория с таким именем уже есть")
            return

        try:
            database.insert_category(category_name)
            self.accept()
            QMessageBox.information(self, "Успех",
                                    "Категория успешно добавлена")

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось добавить категорию: {str(e)}"
            )


class DeleteCategoryDialog(QDialog, DeleteCategoryUI):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 110)

        self.setupUi(self)

        self.get_categories()

        self.buttonBox.accepted.disconnect()
        self.buttonBox.rejected.disconnect()

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

    def get_categories(self):
        combobox = self.comboBox
        categories = database.get_categories()
        for category in categories:
            combobox.addItem(category[0])

    def accept_dialog(self):
        category_name = self.comboBox.currentText()
        if category_name == "Все":
            QMessageBox.warning(self, "Ошибка",
                                "Данную категорию удалить нельзя!")
            return
        if not category_name:
            QMessageBox.warning(self, "Ошибка",
                                "Категория не может быть пустой")
            return

        try:
            database.edit_games_category(
                database.get_category_id_by_name(category_name), 1)

            database.delete_category(
                database.get_category_id_by_name(category_name))
            self.accept()
            QMessageBox.information(self, "Успех",
                                    "Категория успешно удалена")

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось удалить категорию: {str(e)}"
            )
