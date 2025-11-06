from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox, QLineEdit

from db import database
from ui.add_game_dialog import Ui_Dialog as AddGameUI
from ui.createCategory import Ui_Dialog as AddCategoryUI
from ui.deleteCategory import Ui_Dialog as DeleteCategoryUI
from ui.edit_game_dialog_ui import Ui_Dialog as EditGameUI
from ui.profile_dialog_ui import Ui_Dialog as ProfileUI


class BaseDialog:
    def get_categories(self):
        combobox = self.comboBox
        categories = database.get_categories()
        for category in categories:
            combobox.addItem(category[0])


class AddGameDialog(QDialog, AddGameUI, BaseDialog):
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
            self.comboBox.currentText()
        )

        if not game_name:
            QMessageBox.warning(self, "Ошибка", "Введите название игры")
            return

        if not game_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл игры")
            return

        if not category_id:
            category_id = 1

        if not database.check_unique(
            select_from="Games", where_value="name", parameter=game_name
        ):
            QMessageBox.warning(
                self, "Ошибка", "Игра с таким именем уже существует"
            )
            return

        if not database.check_unique(
            select_from="Games", where_value="path", parameter=game_path
        ):
            QMessageBox.warning(
                self, "Ошибка", "Игра с таким путём уке существует"
            )
            return

        try:
            database.insert_game(game_name, game_path, category_id)
            self.accept()
            QMessageBox.information(self, "Успех", "Игра добавлена!")

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось добавить игру: {str(e)}"
            )


class EditGameDialog(QDialog, EditGameUI, BaseDialog):
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
            self.comboBox.currentText()
        )

        if not new_game_name:
            QMessageBox.warning(self, "Ошибка", "Введите название игры")
            return

        if not category_id:
            category_id = 1

        if (
            new_game_name != self.orig_game_name
            and not database.check_name_is_unique(new_game_name)
        ):
            QMessageBox.warning(
                self, "Ошибка", "Игра с таким именем уже существует"
            )
            return

        try:
            database.update_game(
                self.orig_game_name, new_game_name, category_id
            )
            self.accept()
            QMessageBox.information(self, "Успех", "Игра обновлена!")

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось обновить игру: {str(e)}"
            )


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
            QMessageBox.warning(
                self, "Ошибка", "Категория не может быть пустой"
            )
            return

        if category_name == "Все":
            QMessageBox.warning(
                self, "Ошибка", "Нельзя создать категорию с таким именем"
            )
            return

        if not database.insert_category(category_name):
            QMessageBox.warning(
                self, "Ошибка", "Категория с таким именем уже существует"
            )
            return

        self.accept()
        QMessageBox.information(self, "Успех", "Категория успешно добавлена")


class DeleteCategoryDialog(QDialog, DeleteCategoryUI, BaseDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 110)

        self.setupUi(self)

        self.get_categories()

        self.buttonBox.accepted.disconnect()
        self.buttonBox.rejected.disconnect()

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

    def accept_dialog(self):
        category_name = self.comboBox.currentText()
        if category_name == "Все":
            QMessageBox.warning(
                self, "Ошибка", "Данную категорию удалить нельзя!"
            )
            return
        if not category_name:
            QMessageBox.warning(
                self, "Ошибка", "Категория не может быть пустой"
            )
            return

        try:
            database.edit_games_category(
                database.get_category_id_by_name(category_name), 1
            )

            database.delete(
                select_from="Categories",
                where_value="id",
                parameter=database.get_category_id_by_name(category_name),
            )
            self.accept()
            QMessageBox.information(self, "Успех", "Категория успешно удалена")

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось удалить категорию: {str(e)}"
            )


class ProfileDialog(QDialog, ProfileUI):
    def __init__(self):
        super().__init__()
        self.setFixedSize(443, 315)
        self.status = None
        self.login_success = False
        self.setupUi(self)

        self.lineEdit.setPlaceholderText("Введите логин")
        self.lineEdit_2.setPlaceholderText("Введите пароль")
        self.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button.setChecked(True)
        self.status = "Вход"

        self.buttonBox.accepted.disconnect()
        self.buttonBox.rejected.disconnect()

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

        self.forms_button.buttonClicked.connect(self.set_status)

    def set_status(self, button):
        self.status = button.text()
        self.lineEdit.clear()
        self.lineEdit_2.clear()

    def validate_input(self) -> tuple[bool, str]:
        """Проверяет корректность введенных данных"""
        login = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()

        if not login:
            return False, "Введите логин"
        if not password:
            return False, "Введите пароль"
        if len(login) < 3:
            return False, "Логин должен содержать минимум 3 символа"
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        if not login.replace("_", "").isalnum():
            return (
                False,
                "Логин может содержать только буквы, цифры и знак подчеркивания",
            )

        return True, ""

    def accept_dialog(self):
        if not self.status:
            QMessageBox.warning(
                self, "Ошибка", "Выберите действие (Вход или Регистрация)"
            )
            return

        valid, error_msg = self.validate_input()
        if not valid:
            QMessageBox.warning(self, "Ошибка", error_msg)
            return

        login = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()

        if self.status == "Вход":
            if database.users.login_user(login, password):
                QMessageBox.information(
                    self, "Успех", "Вход выполнен успешно!"
                )
                self.login_success = True
                self.accept()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Неверный логин или пароль"
                )
        else:
            if database.users.user_exists(login):
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Пользователь с таким логином уже существует",
                )
                return

            if database.users.register_user(login, password):
                database.users.login_user(login, password)
                QMessageBox.information(self, "Успех", "Регистрация успешна!")
                self.login_success = True
                self.accept()
            else:
                QMessageBox.critical(
                    self, "Ошибка", "Не удалось зарегистрировать пользователя"
                )
