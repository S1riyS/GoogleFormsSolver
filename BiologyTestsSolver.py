import sys
import json
from time import sleep

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    InvalidArgumentException
)
from urllib3.exceptions import NewConnectionError

from functools import wraps
from time import time

letters = {"9а": 0, "9б": 1, "9в": 2}


class GoogleFormParser(object):
    def __init__(self, driver, link, email, class_letter, name):
        self.driver = driver
        self.link = link
        self.email = email
        self.class_letter = class_letter
        self.name = name

    # Собираем все функции в одной
    def parse(self):
        self.go_to_forms_page()
        self.person_identification()
        self.answer_to_questions()

    # Переход на страницу с Google form`ой
    def go_to_forms_page(self):
        try:
            self.driver.get(self.link)
        except InvalidArgumentException:
            print('asAAA')

    # Ввод данных о том, кто проходит тест
    def person_identification(self):
        mail_field, name_field = self.driver.find_elements_by_class_name(
            "quantumWizTextinputPaperinputInput"
        )
        mail_field.send_keys(self.email)
        name_field.send_keys(self.name)

        class_field = self.driver.find_elements_by_class_name(
            "freebirdFormviewerComponentsQuestionRadioChoice"
        )
        class_field[letters[self.class_letter]].click()

        self.go_next()

    # Отвечаем на все вопросы
    def answer_to_questions(self):
        # Конвертация свойства "data-params" блока div в ответ
        def get_answer(data_params):
            data_params_list = data_params.split(",")
            for element in data_params_list:
                if element.startswith('["') and element.endswith('"]'):
                    answer = element[2:-2]
                    break

            if "[" in answer and "]" in answer:
                first_letter = answer[answer.index("[") + 2].upper()
                other_word = answer[answer.index("]") + 1 :]
                return first_letter + other_word
            return answer

        while True:
            try:
                list_item = self.driver.find_elements_by_class_name(
                    "freebirdFormviewerViewNumberedItemContainer"
                )
                for item in list_item:
                    try:
                        input_field = item.find_element_by_class_name(
                            "quantumWizTextinputPaperinputInput"
                        )

                        answer_block = item.find_element_by_class_name("m2")
                        answer = get_answer(answer_block.get_attribute("data-params"))

                        input_field.send_keys(answer)
                    except NoSuchElementException:
                        pass
                self.go_next()

            except AssertionError:
                print("Тест пройден!")
                break

    # Переход на следующую страницу с вопросами
    def go_next(self):
        buttons = self.driver.find_elements_by_class_name(
            "appsMaterialWizButtonPaperbuttonLabel"
        )
        is_next_button_exist = False

        for button in buttons:
            if button.text == "Далее":
                is_next_button_exist = True
                button.click()
                break

        assert is_next_button_exist


    # Отправка формы
    def send_google_form(self):
        buttons = self.driver.find_elements_by_class_name(
            "appsMaterialWizButtonPaperbuttonLabel"
        )
        for button in buttons:
            if button.text == "Отправить":
                button.click()
                break


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("settings.ui", self)
        self.setWindowTitle("Вход")
        self.setFixedSize(400, 310)

        for i in letters:
            self.classBox.addItem(i)

        with open("data.json", "r", encoding='utf8') as read_file:
            data = json.load(read_file)
            self.emailLine.setText(data['email'])
            self.nameLine.setText(data['name'])
            self.classBox.setCurrentText(data['class'])

        self.startButton.clicked.connect(self.start)


    def start(self):
        with open("data.json", "w", encoding='utf8') as outfile:
            data_to_write = {
                "email": self.emailLine.text(),
                "name": self.nameLine.text(),
                "class": self.classBox.currentText(),
            }
            json.dump(data_to_write, outfile)

        try:
            driver = webdriver.Chrome()
            parser = GoogleFormParser(
                driver=driver,
                link=self.linkLine.text(),
                email=self.emailLine.text(),
                class_letter=self.classBox.currentText(),
                name=self.nameLine.text(),
            )
            parser.parse()
        except:
            print('Не верно введен адрес теста')
            driver.close()
            sleep(5)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())

#https://docs.google.com/forms/d/e/1FAIpQLScDRTOmdKDwuSQyfn33a4nbNw0zCqH1VYXhhTxRnfWuFmWhXA/viewform