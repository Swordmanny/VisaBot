import time
from datetime import datetime
from datetime import date
from selenium import webdriver
from pushbullet import PushBullet

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = 'https://www.ch-edoc-reservation.admin.ch/{}'
DT = date(2022, 10, 1)

def make_a_push():
    pb_client = PushBullet("<Your api key>")
    pb_client.push_link("Reserve now", BASE.format('#/session?token=[token]&locale=en-US'))

def is_triggered(earliest):
    return earliest < DT

def login(driver):
    driver.get(BASE.format('#/session?token=Uwpb9nCj&locale=en-US'))

def retrieve(driver):
    driver.find_element(by=By.ID, value="bookingListBtn").click()
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[1]/td[1]"))
    )
    d = datetime.strptime(element.text.split()[1], "%d.%m.%Y").date()
    return d

def append_to_db(data, has_sent):
    with open("db", "a") as f:
        f.write(' '.join([data, has_sent]))
        f.write('\n')

def read_latest():
    try:
        with open("db", "r") as f:
            _, res = f.readlines()[-1].strip().split()
    except Exception as e:
        return '0'
    return res
    

if __name__ == '__main__':
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.headless = True
    # initializing webdriver for Chrome with our options
    driver = webdriver.Chrome(options=options)

    try:
        login(driver)
        d = retrieve(driver)
        has_sent = read_latest()
        if is_triggered(d) and (has_sent == '0'):
            make_a_push()
            append_to_db(d.strftime('%Y-%m-%d'), '1')
        else:
            append_to_db(d.strftime('%Y-%m-%d'), has_sent)

    except Exception as e:
        print(e)
    finally:
        driver.quit()
