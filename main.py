import sys
import os
import sqlite3
import logging
from datetime import datetime
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from image_client import get_one_image


def goto_login_from_welcome():
    login = LoginScreen()
    widget.addWidget(login)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def goto_register_from_welcome():
    register = RegisterScreen()
    widget.addWidget(register)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def goto_main(logged_in=False):
    main = MainScreen(logged_in)
    widget.addWidget(main)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def goto_back():
    previous_index = widget.currentIndex() - 1
    widget.setCurrentIndex(previous_index)
    for widget_index in range(widget.count() - 1, previous_index, -1):
        widget.removeWidget(widget.widget(widget_index))


def logout():
    widget.setCurrentIndex(0)
    for widget_index in range(widget.count() - 1, 0, -1):
        widget.removeWidget(widget.widget(widget_index))


def goto_settings():
    settings = SettingsScreen()
    widget.addWidget(settings)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def goto_advanced_settings():
    advanced_settings = AdvancedSettingsScreen()
    widget.addWidget(advanced_settings)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def confirm_export_popup():
    confirm_export_dialog = ConfirmExportScreen()
    widget.addWidget(confirm_export_dialog)
    widget.setFixedHeight(300)
    widget.setFixedWidth(400)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def cancel_export():
    # goto_back()
    # widget.removeWidget(widget.widget(widget.currentIndex() + 1))
    # widget.update()
    # widget.setFixedHeight(800)
    # widget.setFixedWidth(1200)
    print("canceled")


def confirm_export():
    cancel_export()
    print("confirmed")


def lookup_pinyin(character_index):
    db = sqlite3.connect(char_path)
    cursor = db.cursor()
    result = cursor.execute(f"SELECT pinyin FROM characters WHERE id = '{character_index}'").fetchone()
    cursor.close()
    return result


class WelcomeScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("welcome.ui", self)
        self.login.clicked.connect(goto_login_from_welcome)
        self.new_user.clicked.connect(goto_register_from_welcome)
        self.guest.clicked.connect(self.guest_helper)

    def guest_helper(self):
        goto_main(logged_in=False)


class LoginScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("login.ui", self)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.login_helper)
        self.back.clicked.connect(goto_back)

    def login_helper(self):
        username = self.username_field.text()
        password = self.password_field.text()
        db = sqlite3.connect(path)
        cursor = db.cursor()
        result = cursor.execute(f"SELECT id FROM users WHERE username = '{username}'"
                                f" AND password = '{password}'").fetchone()
        cursor.close()
        if result is not None:
            goto_main(logged_in=True)


class RegisterScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("register.ui", self)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.register_user.clicked.connect(self.register_user_helper)
        self.back.clicked.connect(goto_back)

    def register_user_helper(self):
        username = self.username_field.text()
        password = self.password_field.text()
        db = sqlite3.connect(path)
        cursor = db.cursor()
        # Create the table if it does not exist
        result = cursor.execute(f"SELECT id FROM users WHERE username = '{username}'").fetchone()
        if result is None:
            cursor.execute(f"INSERT INTO users (username, password)"
                           f"VALUES ('{username}', '{password}')")
            db.commit()
            cursor.close()
            goto_back()
        else:
            cursor.close()
            self.dialog = UserAlreadyExists()
            self.dialog.show()


class MainScreen(QDialog):
    def __init__(self, logged_in=False):
        super().__init__()
        loadUi("main.ui", self)
        self.current_index = -1
        self.next_character()
        self.skip_char.clicked.connect(self.next_character)
        self.guess_char_button.clicked.connect(self.guess_char)
        self.settings.clicked.connect(goto_settings)
        self.logout.clicked.connect(self.confirm_logout)
        self.dialog = NewAndExistingFeatures()
        self.dialog.show()

    def confirm_logout(self):
        self.dialog = ConfirmLogoutScreen()
        self.dialog.show()

    def next_character(self):
        image_filepath = get_one_image()
        pixmap = QPixmap(image_filepath)
        self.character_image.setPixmap(pixmap)
        self.current_index = int(self.get_image_index(image_filepath))


    def get_image_index(self, image_filepath):
        return image_filepath.split("/")[-1][:-4]

    def guess_char(self):
        guess = self.char_guess_text.text()
        answer = lookup_pinyin(self.current_index)[0]
        if guess == answer:
            self.dialog = Correct()
        else:
            self.dialog = Incorrect()
        self.dialog.show()
        self.next_character()


class SettingsScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("settings.ui", self)
        self.advanced_settings.clicked.connect(goto_advanced_settings)
        self.back.clicked.connect(goto_back)


class AdvancedSettingsScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("advanced_settings.ui", self)
        # self.confirm_export.hide()
        # self.export_alert.hide()
        # self.export_excel.clicked.connect(self.confirm_export.show)
        # self.export_excel.clicked.connect(self.export_alert.show)
        # self.confirm_export.rejected.connect(self.confirm_export.hide)
        # self.confirm_export.rejected.connect(self.export_alert.hide)
        self.export_excel.clicked.connect(self.confirm_export_popup)
        self.back.clicked.connect(goto_back)
        self.dialog = ConfirmExportScreen()

    def confirm_export_popup(self):
        self.dialog.show()


class Popup(QDialog):
    def __init__(self, template_name):
        super().__init__()
        loadUi(template_name, self)


class NewAndExistingFeatures(Popup):
    def __init__(self):
        super().__init__(template_name="new_and_existing_features.ui")
        self.buttonBox.accepted.connect(self.confirm_tutorial)

    def confirm_tutorial(self):
        self.dialog = HelpWithNewFeatures()
        self.dialog.show()


class HelpWithNewFeatures(Popup):
    def __init__(self):
        super().__init__(template_name="help_with_new_features.ui")


class ConfirmExportScreen(Popup):
    def __init__(self):
        super().__init__(template_name="confirm_export.ui")
        self.buttonBox.accepted.connect(self.confirm_export)

    def confirm_export(self):
        if not os.path.exists(os.path.join(os.getcwd(), "export")):
            os.mkdir("export")
        with open(os.path.join(os.getcwd(), "export", "progress_data.xlsx"), "w") as f:
            pass


class ConfirmLogoutScreen(Popup):
    def __init__(self):
        super().__init__(template_name="confirm_logout.ui")
        self.buttonBox.accepted.connect(logout)


class UserAlreadyExists(Popup):
    def __init__(self):
        super().__init__(template_name="user_already_exists.ui")


class Correct(Popup):
    def __init__(self):
        super().__init__(template_name="correct.ui")


class Incorrect(Popup):
    def __init__(self):
        super().__init__(template_name="incorrect.ui")


def configure_logger(configured_log_dir=None):
    current_date = datetime.now()
    if configured_log_dir is None:
        configured_log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(configured_log_dir):
        os.makedirs(configured_log_dir)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                os.path.join(
                    configured_log_dir,
                    "%s%s%s_%s%s%s.log" % (current_date.year, current_date.month, current_date.day, current_date.hour,
                                           current_date.minute, current_date.second))),
            logging.StreamHandler(sys.stdout)
        ]
    )


def start_app():
    configure_logger()
    logging.debug("Logger configured")
    if not os.path.exists(os.path.join(os.getcwd(), "db")):
        os.mkdir("db")
    db_path = os.path.join(os.getcwd(), "db", "userdata.db")
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    # Create the table if it does not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT unique, password TEXT)")
    db.commit()
    cursor.close()

    char_db_path = os.path.join(os.getcwd(), "db", "character_data.db")
    db = sqlite3.connect(char_db_path)
    cursor = db.cursor()
    # Create the table if it does not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS characters (id INTEGER PRIMARY KEY, pinyin TEXT, meaning TEXT)")
    db.commit()
    cursor.close()

    new_app = QApplication(sys.argv)
    welcome = WelcomeScreen()
    new_widget = QtWidgets.QStackedWidget()
    new_widget.addWidget(welcome)
    new_widget.setFixedHeight(800)
    new_widget.setFixedWidth(1200)
    return new_app, new_widget, db_path, char_db_path


if __name__ == "__main__":
    try:
        app, widget, path, char_path = start_app()
        widget.show()
        sys.exit(app.exec())
    except Exception as err:
        logging.warning(err)
