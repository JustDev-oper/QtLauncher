from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox

from db import database
from ui.add_game_dialog_ui import Ui_Dialog


class AddGameDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(450, 120)

        self.setupUi(self)
        self.path_button.clicked.connect(self.choose_file)

        self.buttonBox.accepted.disconnect()
        self.buttonBox.rejected.disconnect()

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

    def choose_file(self):
        file_path = QFileDialog.getOpenFileName(
            self, 'Выбрать файл', '',
            'EXE - Файл (*.exe)')[0]
        if file_path:
            self.file_path.setText(file_path)

    def accept_dialog(self):
        game_name = self.game_name.text().strip()
        game_path = self.file_path.text().strip()

        if not game_name:
            QMessageBox.warning(self, "Ошибка", "Введите название игры")
            return

        if not game_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл игры")
            return

        if not database.check_name_is_unique(game_name):
            QMessageBox.warning(self, "Ошибка",
                                "Игра с таким именем уже существует")
            return

        if not database.check_path_is_unique(game_path):
            QMessageBox.warning(self, "Ошибка",
                                "Игра с таким путём уке существует")
            return

        try:
            database.insert_game(game_name, game_path)
            self.accept()
            QMessageBox.information(self, "Успех", "Игра добавлена!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось добавить игру: {str(e)}")
