from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import re

CHROME_DRIVER_PATH = ""
USER_AGENT = ""
ACCEPT_LANGUAGE = ""
DOMAIN_URL = ""
MAIN_SEARCHED_WEBSITE = ""
A_TAGS_CLASS = ""
PUBLISH_DATE_ELEMENT = ""
PUBLISH_DATE_CLASS = ""
STREET_ELEMENT = ""
STREET_ELEMENT_CLASS = ""
STREET_ELEMENT2 = ""
STREET_ELEMENT_CLASS2 = ""
CITY_ELEMENT = ""
CITY_ELEMENT_CLASS = ""
PRICE_ELEMENT = ""
PRICE_ELEMENT_CLASS = ""
NEXT_PAGE_SELECTOR = ""
URL_TO_YOUR_GOOGLE_FORM = ""
PUBLISH_DATE_XPATH = ""
ADDRESS_XPATH = ""
PRICE_XPATH = ""
LINK_XPATH = ""
SUBMIT_BUTTON_XPATH = ""


def crawler(website_url, search_object):
    header = {
        "User-Agent": USER_AGENT,
        "Accept-Language": ACCEPT_LANGUAGE
    }

    response_main_page = requests.get(website_url, headers=header)
    data_main_page = response_main_page.text
    soup = BeautifulSoup(data_main_page, "html.parser")

    all_link_elements = soup.find_all(name="a", class_=A_TAGS_CLASS)

    all_links_with_domain = []

    for i in range(len(all_link_elements)):
        all_links_with_domain.append(f"{DOMAIN_URL}{all_link_elements[i].get('href')}")

    for i in range(len(all_links_with_domain)):
        link = all_links_with_domain[i]

        response_inner_page = requests.get(link, headers=header)
        data_inner_page = response_inner_page.text
        soup_inner_page = BeautifulSoup(data_inner_page, "html.parser")

        date = soup_inner_page.find(name=PUBLISH_DATE_ELEMENT, class_=PUBLISH_DATE_CLASS).getText()

        street = ""

        # FOR THE ADDRESS HAD TO DIVIDE IN TWO ELEMENTS, STREET AND CITY, TO GET THE FULL ADDRESS
        if soup_inner_page.find(name=STREET_ELEMENT, class_=STREET_ELEMENT_CLASS):
            street = soup_inner_page.find(name=STREET_ELEMENT, class_=STREET_ELEMENT_CLASS).getText()

        # STREET SHOW UP IN TWO DIFFERENT PLACES DEPENDING
        if street is None:
            street = soup_inner_page.find(name=STREET_ELEMENT2, class_=STREET_ELEMENT_CLASS2).getText()

        # FOR THE CITY ELEMENT HAD TO REMOVE THE SUBSTRING 'location_on' TO CLEAN THE DATA
        city_remove_location = soup_inner_page.select(f".{CITY_ELEMENT_CLASS} {CITY_ELEMENT}")[0].getText()
        city_removing_loc = city_remove_location.replace("location_on", "")
        city = city_removing_loc.strip()

        if street is not None:
            address = remove_emoji(f"{street} {city}")
        else:
            address = remove_emoji(f"{city}")

        price = soup_inner_page.find(name=PRICE_ELEMENT, class_=PRICE_ELEMENT_CLASS).getText()

        search_object["publish_dates"].append(date)
        search_object["addresses"].append(address)
        search_object["prices"].append(price)
        search_object["links"].append(link)

    # SELECTOR FOR THE NEXT PAGES IS AN ID, DOUBLE CHECK IF IT'S AN ID OR A CLASS AND CHANGE ACCORDINGLY
    subsequent_page = soup.find(name="a", id=NEXT_PAGE_SELECTOR)
    search_object["next_page"] = f"{DOMAIN_URL}{subsequent_page.get('href')}"


def fill_form(search_object):
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)

    for values in range(len(search_object["publish_dates"])):
        time.sleep(2)
        driver.get(URL_TO_YOUR_GOOGLE_FORM)

        publish_date = driver.find_element_by_xpath(PUBLISH_DATE_XPATH)
        address = driver.find_element_by_xpath(ADDRESS_XPATH)
        price = driver.find_element_by_xpath(PRICE_XPATH)
        link = driver.find_element_by_xpath(LINK_XPATH)
        submit_button = driver.find_element_by_xpath(SUBMIT_BUTTON_XPATH)

        time.sleep(2)
        publish_date.send_keys(search_object["publish_dates"][values])
        address.send_keys(search_object["addresses"][values])
        price.send_keys(search_object["prices"][values])
        link.send_keys(search_object["links"][values])
        submit_button.click()


def remove_emoji(text):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', text)


def main():
    searched_page = MAIN_SEARCHED_WEBSITE
    first_called = True
    search_results = {
        "publish_dates": [],
        "addresses": [],
        "prices": [],
        "links": [],
        "nex_page": ""
    }

    for i in range(5):
        if first_called:
            print("Is searching the first one")
            print(searched_page)
            crawler(searched_page, search_results)
            first_called = False

        else:
            print("Is searching the second and on")
            searched_page = search_results["next_page"]
            print(searched_page)
            search_results = {
                "publish_dates": [],
                "addresses": [],
                "prices": [],
                "links": [],
                "nex_page": ""
            }
            crawler(searched_page, search_results)

        fill_form(search_results)


main()
