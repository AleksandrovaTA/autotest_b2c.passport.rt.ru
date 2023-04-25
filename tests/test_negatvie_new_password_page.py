from pages.api_reg_email import RegEmail
from pages.auth import *
from selenium.webdriver.common.by import By
from pages.settings import *
import time
import pytest
from selenium.webdriver.common.keys import Keys


@pytest.mark.newpass
@pytest.mark.negative
def test_forgot_password_page(browser):
    """Проверка восстановления пароля по почте - негативные сценарии."""
    sign_at = valid_email.find('@')
    mail_name = valid_email[0:sign_at]
    mail_domain = valid_email[sign_at + 1:len(valid_email)]

    page = NewPassPage(browser)
    page.enter_username(valid_email)
    time.sleep(20)
    page.btn_click_continue()

    time.sleep(30)

    """Извлекаем ID последнего письма"""
    result_id, status_id = RegEmail().get_id_letter(mail_name, mail_domain)
    id_letter = result_id[0].get('id')
    assert status_id == 200, "status_id error"
    assert id_letter > 0, "id_letter > 0 error"

    result_code, status_code = RegEmail().get_reg_code(mail_name, mail_domain, str(id_letter))

    text_body = result_code.get('body')
    reg_code = text_body[text_body.find('Ваш код: ') + len('Ваш код: '):
                         text_body.find('Ваш код: ') + len('Ваш код: ') + 6]
    assert status_code == 200, "status_code error"
    assert reg_code != '', "reg_code != [] error"

    reg_digit = [int(char) for char in reg_code]
    print(reg_digit)
    browser.implicitly_wait(30)
    for i in range(0, 6):
        browser.find_elements(*NewPassLocators.NEWPASS_ONETIME_CODE)[i].send_keys(reg_code[i])
        browser.implicitly_wait(5)
    time.sleep(10)

    elem_new_pass = browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS)
    elem_conf_pass = browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS_CONFIRM)

    def input_new_pass(new_pass):
        # browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS).clear()
        elem_new_pass.send_keys(Keys.COMMAND, 'a')
        elem_new_pass.send_keys(Keys.DELETE)
        elem_new_pass.send_keys(new_pass)
        time.sleep(3)
        # browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS_CONFIRM).clear()
        elem_conf_pass.send_keys(Keys.COMMAND, 'a')
        elem_conf_pass.send_keys(Keys.DELETE)
        elem_conf_pass.send_keys(new_pass)
        time.sleep(3)

    """1. Новый пароль - менее 8 символов"""
    new_pass = valid_pass_reg[0:7]
    input_new_pass(new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Длина пароля должна быть не менее 8 символов'

    """2. Новый пароль - более 20 символов"""
    new_pass = valid_pass_reg[0:7]*3
    input_new_pass(new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Длина пароля должна быть не более 20 символов'

    """3. Новый пароль - пароль не содержит заглавные буквы"""
    new_pass = valid_pass_reg.lower()
    input_new_pass(new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Пароль должен содержать хотя бы одну заглавную букву'

    """4. Новый пароль - пароль не содержит строчные буквы"""
    new_pass = valid_pass_reg.upper()
    input_new_pass(new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Пароль должен содержать хотя бы одну прописную букву'


    """5. Новый пароль - пароль не содержит ни одной цифры или спецсимвола"""
    new_pass = valid_pass_reg
    for i in new_pass:
        if i.isdigit() or i in special_chars():
            new_pass = new_pass.replace(i, 'x')
    input_new_pass(new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Пароль должен содержать хотя бы 1 спецсимвол или хотя бы одну цифру'



