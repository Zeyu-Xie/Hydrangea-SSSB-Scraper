from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

INF = 2**31 - 1

driver = webdriver.Chrome()
driver.set_page_load_timeout(INF)


class Apartment:

    global driver

    def __get_apartment_attribute(self, XPATH, position):
        WebDriverWait(driver, INF).until(lambda d: d.find_element(By.XPATH, XPATH))
        if position == "text":
            return driver.find_element(By.XPATH, XPATH).text
        elif position == "href":
            return driver.find_element(By.XPATH, XPATH).get_attribute("href")
        else:
            return "1"

    def __init__(self, link):

        driver.get(link)
        # Title
        self.title = self.__get_apartment_attribute(
            XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[2]/h1',
            position="text",
        )
        # Object Number
        self.object_number = self.__get_apartment_attribute(
            XPATH='//*[@id="SubNavigationContentContainer"]/div[1]/div[2]/h5/em',
            position="text",
        )
        self.link = link

    def print_info(self):
        print(self.title, self.object_number)


def get_apartment_link_list():
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


if __name__ == "__main__":

    apartment_link_list = get_apartment_link_list()
    print(len(apartment_link_list))

    apartment_1 = Apartment(apartment_link_list[0])
    apartment_1.print_info()
