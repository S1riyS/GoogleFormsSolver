from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class GoogleFormParser(object):
    def __init__(self, driver, link, email, class_letter, name):
        self.driver = driver
        self.link = link
        self.letters = {'9а': 0, '9б': 1, '9в': 2}
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
        self.driver.get(self.link)

    # Ввод данных о том, кто проходит тест
    def person_identification(self):
        mail_field, name_field = self.driver.find_elements_by_class_name('quantumWizTextinputPaperinputInput')
        mail_field.send_keys(self.email)
        name_field.send_keys(self.name)

        class_field = self.driver.find_elements_by_class_name('freebirdFormviewerComponentsQuestionRadioChoice')
        class_field[self.letters[self.class_letter]].click()

        self.go_next()

    # Отвечаем на все вопросы
    def answer_to_questions(self):
        # Конвертация свойства блока в ответ
        def get_answer(line):
            answer_element = line.split(',')[10][2:-2]
            if "[" in answer_element and "]" in answer_element:
                first_letter = answer_element[answer_element.index('[') + 1]
                other_word = answer_element[answer_element.index(']') + 1:]
                return first_letter + other_word
            return answer_element

        while True:
            try:
                list_item = self.driver.find_elements_by_class_name('freebirdFormviewerViewNumberedItemContainer')
                for item in list_item:
                    try:
                        input_field = item.find_element_by_class_name('quantumWizTextinputPaperinputInput')

                        answer_block = item.find_element_by_class_name('m2')
                        answer = get_answer(answer_block.get_attribute('data-params'))

                        input_field.send_keys(answer)

                    except NoSuchElementException:
                        print('No such element')

                self.go_next()

            except AssertionError as e:
                print('Тест пройден!')

    # Переход на следующую страницу с вопросами
    def go_next(self):
        buttons = self.driver.find_elements_by_class_name('appsMaterialWizButtonPaperbuttonLabel')
        is_next_button_exist = False

        for button in buttons:
            if button.text == 'Далее':
                is_next_button_exist = True
                button.click()
                break

        if not is_next_button_exist:
            raise AssertionError

    # Отправка формы
    def send_google_form(self):
        buttons = self.driver.find_elements_by_class_name('appsMaterialWizButtonPaperbuttonLabel')
        for button in buttons:
            if button.text == 'Отправить':
                button.click()
                break


driver = webdriver.Chrome()
parser = GoogleFormParser(
    driver=driver,
    link='https://docs.google.com/forms/d/e/1FAIpQLSfzGU0C8qpeC9eabn_mKTmkba60kGUn0ukWTgXslpz1pg06XQ/viewform',
    email='kirill.ankudinov.94@mail.ru',
    class_letter='9б',
    name='Анкудинов Кирилл'
)
parser.parse()
