import json
from pushbullet import PushBullet
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

BASE = 'https://ais.usvisa-info.com/en-ca/niv/{}'
code_to_city = ["Calgary", "Halifax", "Montreal", "Ottawa", "Quebec City", "Toronto", "Vancouver"]

def is_triggered(city, before_datetime, retrieve_list):
    index = code_to_city.index(city)
    found_datetime_str = retrieve_list[index]
    if found_datetime_str != 'NA':
        found_datetime = datetime.strptime(retrieve_list[index], '%Y-%m-%d')
        if before_datetime > found_datetime: 
            return True
    return False

def maybe_make_a_push(city, date):
    pb_client = PushBullet()
    pb_client.get_push()


def login(driver):
    driver.get(BASE.format('users/sign_in'))
    driver.find_element(by=By.XPATH, value="//input[@id='user_email']").send_keys('<email>')
    driver.find_element(by=By.XPATH, value="//input[@id='user_password']").send_keys('<password>')
    checkbox = driver.find_element(by=By.XPATH, value="//input[@id='policy_confirmed']")
    ActionChains(driver).move_to_element(checkbox).click(checkbox).perform()
    driver.find_element(by=By.XPATH, value="//input[@type='submit']").click()

def switch(driver, is_travel):
    driver.get(BASE.format('schedule/39969417/applicants/47148478/edit'))
    path = "//input[@id='applicant_traveling_to_apply_{}']"
    true_box, false_box = driver.find_element(by=By.XPATH, value=path.format("true")), driver.find_element(by=By.XPATH, value=path.format("false"))
    if is_travel:
        ActionChains(driver).move_to_element(true_box).click(true_box).perform()
    else:
        ActionChains(driver).move_to_element(false_box).click(false_box).perform()
    driver.find_element(by=By.XPATH, value="//input[@type='submit']").click()


def retrieve(driver):
    start_code = 89
    res = []
    for i, city in enumerate(code_to_city):
        driver.get(BASE.format('schedule/39969417/appointment/days/{}.json?appointments[expedite]=false'.format(start_code + i)))
        result = driver.find_element(By.TAG_NAME, 'pre')
        dates = json.loads(result.text)
        if len(dates):
            res.append(dates[0]['date'])
        else:
            res.append('NA')
    return res

def append_to_db(data):
    with open("db", "a") as f:
        f.write(','.join(data))
        f.write('\n')

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
        current_ts = datetime.now().strftime('%x %X')
        switch(driver, is_travel=True)
        res = retrieve(driver)
        append_to_db([current_ts, 'true'] + res)
        switch(driver, is_travel=False)
        res = retrieve(driver)
        append_to_db([current_ts, 'false'] + res)
    except Exception as e:
        print(e)
    finally:
        driver.quit()
