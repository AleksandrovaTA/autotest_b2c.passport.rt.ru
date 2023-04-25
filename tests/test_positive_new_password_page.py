from pages.api_reg_email import RegEmail
from pages.auth import *
from selenium.webdriver.common.by import By
from pages.settings import *
import time
import pytest


@pytest.mark.newpass
@pytest.mark.positive
def test_forgot_password_page(browser):
    """Проверка восстановления пароля по почте."""
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

    """Получаем код регистрации из письма от Ростелекома"""
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
    # browser.implicitly_wait(30)
    time.sleep(10)
    new_pass = fake_password
    browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS).send_keys(new_pass)
    time.sleep(3)
    browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS_CONFIRM).send_keys(new_pass)
    browser.find_element(*NewPassLocators.NEWPASS_BTN_SAVE).click()
    time.sleep(60)
    print(browser.current_url)

    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/required-action'

    """В случае успешной смены пароля, перезаписываем его в файл settings"""
    with open(r"../pages/settings.py", 'r', encoding='utf8') as file:
        lines = []
        for line in file.readlines():
            if 'valid_pass_reg' in line:
                lines.append(f"valid_pass_reg = '{fake_password}'\n")
            else:
                lines.append(line)
    with open(r"../pages/settings.py", 'w', encoding='utf8') as file:
        file.writelines(lines)