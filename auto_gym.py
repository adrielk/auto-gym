from datetime import datetime
from time import sleep
from platform import system
from sys import argv
from os.path import isfile

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

'''
GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS GAINS
'''

OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--headless")
OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])

print(f'System: {system()}')

if system() == 'Linux':
    DRIVER = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=OPTIONS)
else:
    DRIVER = webdriver.Chrome(executable_path='./chromedriver', options=OPTIONS)
PROGRAMS_PAGE_URL = 'https://www.go.recsports.virginia.edu/Program/GetProducts?classification=cc3e1e17-d2e4-4bdc-b66e-7c61999a91bf'
NETBADGE_LOGIN_URL = 'https://shibidp.its.virginia.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1'

DAYS = ['None', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def login(username, password):
    wait_time = 10  # seconds

    DRIVER.get(PROGRAMS_PAGE_URL)
    
    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'loginLink')))
    except TimeoutException:
        # User already logged in
        return 0

    DRIVER.find_element_by_id('loginLink').click()

    try:
        netbadge_login_button_xpath = '/html/body/div[3]/div[4]/div/div/div/div[2]/div[2]/div[2]/div/button'
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.XPATH, netbadge_login_button_xpath)))
    except TimeoutException:
        print('Can\'t find NetBadge login button.')
        return 1

    DRIVER.execute_script("submitExternalLoginForm('Shibboleth')")

    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'user')))
    except TimeoutException:
        print('Can\'t find username/password field.')
        return 1

    DRIVER.find_element_by_id('user').send_keys(username)
    DRIVER.find_element_by_id('pass').send_keys(password)
    DRIVER.find_element_by_name('_eventId_proceed').click()

    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'duo_iframe')))
    except TimeoutException:
        print('Can\'t find Duo iframe.')
        return 1

    DRIVER.switch_to.frame('duo_iframe')

    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.NAME, 'dampen_choice')))
    except TimeoutException:
        print('Can\'t find remember me checkbox.')
        return 1

    DRIVER.find_element_by_name('dampen_choice').click()
    duo_login_button_xpath = '/html/body/div/div/div[1]/div/form/div[1]/fieldset/div[1]/button'
    DRIVER.find_element_by_xpath(duo_login_button_xpath).click()

    wait_time = 10 * 60  # minutes * 60 seconds/min
    try:
        print('Waiting for DUO login.')
        WebDriverWait(DRIVER, wait_time).until(lambda driver: driver.current_url == PROGRAMS_PAGE_URL)
    except TimeoutException:
        print('DUO login timed out.')
        return 1
    else:
        print('DUO Login approved.')

    return 0


def find_reservation(preferred_time, days_list):
    BASE_STRING = "https://www.go.recsports.virginia.edu"
    DRIVER.get(BASE_STRING + '/Program/GetProducts')

    gymButton = DRIVER.find_element_by_id('cc3e1e17-d2e4-4bdc-b66e-7c61999a91bf')
    gymButton.click()

    week_xPath_prefix = '/html/body/div[3]/div[1]/div[2]/section/div/div[2]/div/div/div/'
    mondayButton_xPath = week_xPath_prefix + 'div[1]/div'
    tuesdayButton_xPath = week_xPath_prefix + 'div[2]/div'
    wednesdayButton_xPath = week_xPath_prefix + 'div[3]/div'
    thursdayButton_xPath = week_xPath_prefix + 'div[4]/div'
    fridayButton_xPath = week_xPath_prefix + 'div[5]/div'
    saturdayButton_xPath = week_xPath_prefix + 'div[6]/div'
    sundayButton_xPath = week_xPath_prefix + 'div[7]/div'

    days_button_paths = [mondayButton_xPath, tuesdayButton_xPath, wednesdayButton_xPath, thursdayButton_xPath,
                         fridayButton_xPath, saturdayButton_xPath, sundayButton_xPath]

    closed_text = "No Spots Available"  # subject to change

    try:
        WebDriverWait(DRIVER, 5).until(expected_conditions.presence_of_element_located((By.ID, 'list-group')))
    except TimeoutException:
        print("Timeout")

    for day_path in days_button_paths:
        day_num = days_button_paths.index(day_path) + 1
        if str(day_num) in days_list:
            button = DRIVER.find_element_by_xpath(day_path)
            button_onclick = button.get_attribute("onclick")
            button_path = BASE_STRING + button_onclick[button_onclick.index("'") + 1:-1]
            DRIVER.get(button_path)

            try:
                WebDriverWait(DRIVER, 5).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, '/html/body/div[3]/div[1]/div[2]/section/div/div/p')))
            except TimeoutException:
                try:
                    for reservationTime in range(1, 28):
                        r_elem_path = '/html/body/div[3]/div[1]/div[2]/section/div[' + str(reservationTime) + ']'
                        WebDriverWait(DRIVER, 5) \
                            .until(expected_conditions.presence_of_element_located((By.XPATH, r_elem_path)))

                        closed_elem_path = '/html/body/div[3]/div[1]/div[2]/section/div[' + str(
                            reservationTime) + ']/div/div/div/small/span/small'
                        register_elem_path = '/html/body/div[3]/div[1]/div[2]/section/div[' + str(
                            reservationTime) + ']/div/div/div[2]/button'
                        time_elem_path = '/html/body/div[3]/div[1]/div[2]/section/div[' + str(
                            reservationTime) + ']/div/div/div[1]/small'

                        try:
                            WebDriverWait(DRIVER, 5).until(
                                expected_conditions.presence_of_element_located((By.XPATH, closed_elem_path)))
                            message_elem = DRIVER.find_element_by_xpath(closed_elem_path)
                            message_text = message_elem.text
                            time_elem = DRIVER.find_element_by_xpath(time_elem_path)
                            time_elem_text = time_elem.text[0:time_elem.text.index('-')].strip()
                            if time_elem_text == preferred_time:
                                if message_text != closed_text:
                                    if purchase(register_elem_path) == 0:
                                        print('Reservation success!')
                                        break
                                    else:
                                        print('Reservation failed.')
                                else:
                                    print(f'No open slots for {DAYS[day_num]} at time {preferred_time}.')
                                    break

                        except TimeoutException:
                            print('TIMEOUT ERROR')

                except TimeoutException:
                    print(f'No open slots for {DAYS[day_num]} at time {preferred_time}.')
            else:
                print(f'Slots not open yet for {DAYS[day_num]}.')

            DRIVER.get(
                'https://www.go.recsports.virginia.edu/Program/GetProducts?classification=cc3e1e17-d2e4-4bdc-b66e-7c61999a91bf')


def purchase(register_button_xpath):
    wait_time = 10*3  # seconds

    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.XPATH, register_button_xpath)))
    except TimeoutException:
        print('Can\'t find register button. (You may have already registered).')
        return 1

    DRIVER.find_element_by_xpath(register_button_xpath).click()

    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'rbtnYes')))
    except TimeoutException:
        print('Can\'t find Yes button.')
        return 1

    DRIVER.find_element_by_id('rbtnYes').click()

    add_to_cart_form_xpath = '/html/body/div[3]/div[1]/div[2]/form[2]'
    DRIVER.find_element_by_xpath(add_to_cart_form_xpath).submit()
    
    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'checkoutButton')))
    except TimeoutException:
        print('Can\'t find checkout button.')
        return 1

    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'gdpr-cookie-accept')))
    except TimeoutException:
        print('No cookies')
    else:
        DRIVER.find_element_by_id('gdpr-cookie-accept').click()

    DRIVER.find_element_by_id('checkoutButton').click()

    try:
        checkout_payment_button_xpath = '/html/body/div[3]/div[1]/div[2]/div[5]/div/div/div[2]/div/div[2]/button'
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.XPATH, checkout_payment_button_xpath)))
    except TimeoutException:
        print('Can\'t find checkout payment button.')
        return 1

    DRIVER.execute_script('Submit()')

    return 0


def getCurrentTime():
    time = datetime.now().strftime("%I:%M %p")
    if time.startswith('0'):
        time = time[1:]
    return time


def main():
    if len(argv) != 2:
        print('Please pass an account config filename.')
        return 1
    if isfile(f'accounts/{argv[1]}'):
        filename = f'accounts/{argv[1]}'
    elif isfile(argv[1]):
        filename = argv[1]
    else:
        print(f'Could not find file {argv[1]}')
        return 1

    with open(filename) as f:
        username = f.readline().strip()
        password = f.readline().strip()
        times_and_days_list = f.readlines()
        times_days_dict = {}
        for time_and_days in times_and_days_list:
            if time_and_days:
                desired_time, days = time_and_days.split(' ')
                desired_time = datetime.strptime(desired_time, "%I:%M%p").strftime("%I:%M %p")
                if desired_time.startswith('0'):
                    desired_time = desired_time[1:]
                days = list(days.strip())
                times_days_dict[desired_time] = days
        try:
            for _ in range(5):  # try 5 times
                for time, days in times_days_dict.items():
                    if login(username, password) != 0:
                        print('Unable to login.')
                    find_reservation(time, days)

            while 1:
                if getCurrentTime() not in times_days_dict.keys():
                    sleep(30)
                else:
                    for _ in range(5):  # try 5 times
                        for time, days in times_days_dict.items():
                            if login(username, password) != 0:
                                print('Unable to login.')
                            find_reservation(time, days)
        except KeyboardInterrupt:
            print('Exited by user.')
        

if __name__ == '__main__':
    main()

DRIVER.quit()
