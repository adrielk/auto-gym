import sys
from datetime import datetime
import time as tm

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

#for raspi os, use following path: /usr/lib/chromium-browser/chromedriver
DRIVER = webdriver.Chrome(executable_path='./chromedriver_win32/chromedriver', options=OPTIONS)
PROGRAMS_PAGE_URL = 'https://www.go.recsports.virginia.edu/Program/GetProducts?classification=cc3e1e17-d2e4-4bdc-b66e-7c61999a91bf'
NETBADGE_LOGIN_URL = 'https://shibidp.its.virginia.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1'
DUO_IFRAME = 'duo_iframe'

#To do:
#Detect OS to configure chromedriver path
#Optimimize by running at selected times (For instance, 4:25 PM every day for 10 iterations)
#update repo for usage details and comments

def login(username, password):

    wait_time = 10

    DRIVER.get(PROGRAMS_PAGE_URL)
    
    try:
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'loginLink')))
    except TimeoutException:
        print('User already logged in')
        return 1

    DRIVER.find_element_by_id('loginLink').click()

    try:
        netbadge_login_button_xpath = '/html/body/div[3]/div[4]/div/div/div/div[2]/div[2]/div[2]/div/button'
        WebDriverWait(DRIVER, wait_time) \
            .until(expected_conditions.presence_of_element_located((By.XPATH, netbadge_login_button_xpath)))
    except TimeoutException:
        print('Can\'t find NetBadge login button.')
        return 1

    DRIVER.execute_script("submitExternalLoginForm('Shibboleth')")

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

    DRIVER.find_element_by_name('dampen_choice').click()
    duo_login_button_xpath = '/html/body/div/div/div[1]/div/form/div[1]/fieldset/div[1]/button'
    DRIVER.find_element_by_xpath(duo_login_button_xpath).click()

    wait_time = 10 * 60  # minutes * 60 seconds/min
    try:
        WebDriverWait(DRIVER, wait_time).until(lambda driver: driver.current_url == PROGRAMS_PAGE_URL)
    except TimeoutException:
        print('DUO login timed out.')
        return 1

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
    # preferred_time = "9:00 PM"

    try:
        WebDriverWait(DRIVER, 5).until(expected_conditions.presence_of_element_located((By.ID, 'list-group')))
    except TimeoutException:
        print("Timeout")

    for day_path in days_button_paths:
        day_num = days_button_paths.index(day_path)+1
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

                            if message_text != closed_text and time_elem_text == preferred_time:
                                if purchase(register_elem_path) == 0:
                                    print('Reservation success!')
                                    break
                                else:
                                    print('Reservation failed.')

                        except TimeoutException:
                            print("ERROR")

                except TimeoutException:
                    print("No time")

            DRIVER.get(
                'https://www.go.recsports.virginia.edu/Program/GetProducts?classification=cc3e1e17-d2e4-4bdc-b66e-7c61999a91bf')
        else:
            print("Invalid Day")


def purchase(register_button_xpath):
    DRIVER.find_element_by_xpath(register_button_xpath).click()

    wait_time = 10  # seconds
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
    return datetime.now().strftime("%I:%M %p")

def main():
    if len(sys.argv) != 5:
        print('Pass username, password, and time as command line arguments. Format time as: "4:30 PM". Format days as 1,2,3,4,5,6,7 where Monday is 1 ')
        return
    username, password, time, days = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    
    days_list = [day.strip() for day in days.split(',')]
    desired_time = datetime.strptime(time, "%I:%M %p").strftime("%I:%M %p")
    current_time = getCurrentTime()
    

    while True:
        while(current_time != desired_time):
            current_time = getCurrentTime()
            print(current_time)
            tm.sleep(30)
        login(username, password)        
        find_reservation(time,days_list)

        current_time = getCurrentTime()

        # if login(username, password) == 0:
        #     find_reservation(time, days_list)
        # else:
        #     print('Login failed.')
        


if __name__ == '__main__':
    main()

DRIVER.quit()
