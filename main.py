from datetime import datetime
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import sys

INF = 2**31 - 1

driver = webdriver.Chrome()
driver.set_page_load_timeout(INF)


def print_log(msg):
    log = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]}] {msg}"
    print(log)


class Apartment:

    global driver

    def __get_attribute(self, XPATH, position):
        WebDriverWait(driver, INF).until(lambda d: d.find_element(By.XPATH, XPATH))
        try:
            if position == "text":
                WebDriverWait(driver, INF).until(
                    lambda d: d.find_element(By.XPATH, XPATH).text != ""
                )
                return driver.find_element(By.XPATH, XPATH).text
            elif position == "href":
                WebDriverWait(driver, INF).until(
                    lambda d: d.find_element(By.XPATH, XPATH).get_attribute("href")
                    != ""
                )
                return driver.find_element(By.XPATH, XPATH).get_attribute("href")
            else:
                return ""
        except Exception as e:
            return None

    def __init__(self, link):

        global driver
        driver.get(link)

        # Title
        self.title = self.__get_attribute(
            XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[2]/h1',
            position="text",
        )
        # Object Number
        self.object_number = self.__get_attribute(
            XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[2]/h5/em',
            position="text",
        )
        # Housing Area
        self.housing_area = {
            "name": self.__get_attribute(
                XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[5]/div/div/dl/dd[2]/a',
                position="text",
            ),
            "link": self.__get_attribute(
                XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[5]/div/div/dl/dd[2]/a',
                position="href",
            ),
        }
        # Address
        self.address = self.__get_attribute(
            XPATH="//dd[contains(@class, 'ObjektAdress')]",
            position="text",
        )
        # Type of Accommodation
        self.type_of_accommodation = self.__get_attribute(
            XPATH="//dd[contains(@class, 'ObjektTyp')]",
            position="text",
        )
        # Living Space
        self.living_space = self.__get_attribute(
            XPATH="//dd[contains(@class, 'ObjektYta')]",
            position="text",
        )
        # Floor
        self.floor = self.__get_attribute(
            XPATH="//dd[contains(@class, 'ObjektVaning')]",
            position="text",
        )
        # Monthly Rent
        self.monthly_rent = self.__get_attribute(
            XPATH="//dd[contains(@class, 'ObjektHyra')]",
            position="text",
        )
        # Elevator
        self.elevator = self.__get_attribute(
            XPATH="//dd[contains(@class, 'ObjektHiss')]",
            position="text",
        )
        # The Rental Agreement is Valid From
        self.rental_agreement_valid_from = self.__get_attribute(
            XPATH="//dd[contains(@class, 'ObjektInflytt')]",
            position="text",
        )
        # Booking Status
        _booking_status_string = self.__get_attribute(
            XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[8]',
            position="text",
        )
        _booking_status_word_list = _booking_status_string.split(" ")
        _booking_status_number_list = []
        for word in _booking_status_word_list:
            try:
                _booking_status_number_list.append(int(word))
            except:
                continue
        self.booking_status = {
            "bookings": _booking_status_number_list[0],
            "highest_credit_days": _booking_status_number_list[1],
        }
        # Application Deadline
        _application_deadline = self.__get_attribute(
            XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[10]/div',
            position="text",
        )
        _application_deadline_word_list = _application_deadline.split(" ")
        _application_deadline_number_list = []
        for index, word in enumerate(_application_deadline_word_list):
            if re.match(r"\d{4}-\d{2}-\d{2}", word):
                _application_deadline_number_list.append(word)
                _application_deadline_number_list.append(
                    _application_deadline_word_list[index + 2].split(".")[0]
                )
                break
        self.application_deadline = {
            "date": _application_deadline_number_list[0],
            "time": _application_deadline_number_list[1],
        }
        self.link = link

    def to_object(self):
        return {
            "title": self.title,
            "object_number": self.object_number,
            "housing_area": self.housing_area,
            "address": self.address,
            "type_of_accommodation": self.type_of_accommodation,
            "living_space": self.living_space,
            "floor": self.floor,
            "monthly_rent": self.monthly_rent,
            "elevator": self.elevator,
            "rental_agreement_valid_from": self.rental_agreement_valid_from,
            "booking_status": self.booking_status,
            "application_deadline": self.application_deadline,
            "link": self.link,
        }

    def _to_csv_row(self):
        _csv_row_str = f"{self.title}, {self.object_number}, {self.housing_area['name']}, {self.housing_area['link']}, {self.address}, {self.type_of_accommodation}, {self.living_space}, {self.floor}, {self.monthly_rent}, {self.elevator}, {self.rental_agreement_valid_from}, {self.booking_status['bookings']}, {self.booking_status['highest_credit_days']}, {self.application_deadline['date']}, {self.application_deadline['time']}, {self.link}"
        return _csv_row_str


def _get_apartment_link_list():
    global driver
    driver.get(
        "https://sssb.se/en/looking-for-housing/apply-for-apartment/available-apartments/?pagination=0&paginationantal=0"
    )
    WebDriverWait(driver, INF).until(
        lambda d: d.find_element(By.CLASS_NAME, "media-body")
    )
    media_body_list = driver.find_elements(By.CLASS_NAME, "media-body")
    apartment_link_list = []
    for media_body in media_body_list:
        apartment_link_list.append(
            media_body.find_element(By.TAG_NAME, "a").get_attribute("href")
        )
    return apartment_link_list


def main():
    apartment_link_list = []
    apartment_list = []

    # Get apartment links
    try:
        apartment_link_list = _get_apartment_link_list()
        n = len(apartment_link_list)
        print_log(f"Get {n} apartment links")
    except Exception as e:
        print_log(e)
        return (e, {})

    # Get apartment information
    for index, apartment_link in enumerate(apartment_link_list):
        try:
            print_log(f"Get apartment {index + 1}/{len(apartment_link_list)}")
            apartment = Apartment(apartment_link)
            apartment_list.append(apartment)
            print_log(f"Success")
        except Exception as e:
            print_log(e)

    return ("Success", apartment_list)


def save_to_json(apartment_list):
    with open(
        f"apartment_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json", "w"
    ) as f:
        json.dump(
            [apartment.to_object() for apartment in apartment_list],
            f,
            indent=4,
            ensure_ascii=False,
        )


def save_to_csv(apartment_list):
    with open(
        f"apartment_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w"
    ) as f:
        f.write(
            "title, object_number, housing_area_name, housing_area_link, address, type_of_accommodation, living_space, floor, monthly_rent, elevator, rental_agreement_valid_from, booking_status_bookings, booking_status_highest_credit_days, application_deadline_date, application_deadline_time, link\n"
        )
        for apartment in apartment_list:
            f.write(apartment._to_csv_row() + "\n")


if __name__ == "__main__":

    print_log("Start getting apartment information")
    status, apartment_list = main()
    if status != "Success":
        print_log("Script ended with error")
        sys.exit(1)
    print_log("Finish getting apartment information")
    save_to_json(apartment_list)
    print_log("Save to json")
    save_to_csv(apartment_list)
    print_log("Save to csv")
