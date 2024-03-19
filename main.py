import requests
import datetime
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import sys

"""
    Get the day of the week for a given date string.

    :param date_str: A string representing a date in the format 'YYYY-MM-DD'.
    :return: A string representing the day of the week corresponding to the input date.
"""
def get_day_of_week(date_str):
    # Parse the date string into a datetime object
    date_object = datetime.strptime(date_str, '%Y-%m-%d')

    # Get the day of the week as an integer (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    day_of_week = date_object.weekday()

    # Define a list of days of the week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    day = days[day_of_week]

    # Return the day of the week corresponding to the integer value
    return str(day)

def reserve_barrys_class(username, password, class_id, class_spot):

    reservation_url = "https://barrysbootcamp.marianaiframes.com/iframe/classes/" + class_id + "/reserve"
    driver = webdriver.Chrome()
    driver.get(reservation_url)
    sleep(2)
    driver.find_element(By.CSS_SELECTOR, "button[data-test-button='log-in']").click()
    ## Barry's Bootcamp Login ##
    username_textbox = driver.find_element("name", "username")
    username_textbox.send_keys(username)

    password_textbox = driver.find_element("name", "password")
    password_textbox.send_keys(password)

    driver.find_element(By.CSS_SELECTOR, "button[data-test-button='log-in']").click()
    sleep(7)
    driver.find_element(By.CSS_SELECTOR, "button[data-test-button='accept-all-cookies']").click()

    v = "//*[contains(text(), '" + class_spot + "')]"
    driver.find_element(By.XPATH, v).click()
    sleep(2)
    driver.find_element(By.CSS_SELECTOR, "button[data-test-button='reserve']").click()
    sleep(5)

def barrys_bootcamp_spot_finder(username, password):
    class_id_url_base = "https://barrysbootcamp.marianatek.com/api/customer/v1/classes"
    layout_url_base = "https://barrysbootcamp.marianatek.com/api/customer/v1/classes/{}"

    date = datetime.today() + timedelta(weeks=1)
    date_str = date.strftime("%Y-%m-%d")
    day_of_week = get_day_of_week(date_str)

    with requests.session() as s:
        params = {
            "min_start_date": date_str,
            "max_start_date": date_str,
            "page_size": 500,
            "location": 9628,
            "region": 9639
        }
        r = s.get(class_id_url_base, params=params)
        data = r.json()

        for result in data.get('results', []):
            if result['start_time'] == '07:30:00':
                class_unique_id = result['id']
                class_layout_url = layout_url_base.format(class_unique_id)
                r = s.get(class_layout_url)
                layout_data = r.json().get('layout', {})

                for spot in layout_data.get('spots', []):
                    spot_available_data = spot.get('is_available', False)
                    spot_name = spot['name']
                    if spot_available_data:
                        if day_of_week == 'Sunday' and 'DF' in spot_name:
                            reserve_barrys_class(username, password, result['id'], spot_name)
                            return
                        elif day_of_week in {'Monday', 'Wednesday', 'Thursday', 'Saturday'} and 'DF' in spot_name:
                            reserve_barrys_class(username, password, result['id'], spot_name)
                            return
                        elif day_of_week == 'Friday' and ('DF' not in spot_name or 'F' in spot_name):
                            reserve_barrys_class(username, password, result['id'], spot_name)
                            return
def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    # Call your function with username and password
    barrys_bootcamp_spot_finder(username, password)

if __name__ == "__main__":
    main()
