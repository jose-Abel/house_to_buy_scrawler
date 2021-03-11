from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time

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
CITY_ELEMENT = ""
CITY_ELEMENT_CLASS = ""
PRICE_ELEMENT = ""
PRICE_ELEMENT_CLASS = ""
NEXT_PAGE_SELECTOR = ""


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

        # FOR THE ADDRESS HAD TO DIVIDE IN TWO ELEMENTS, STREET AND CITY, TO GET THE FULL ADDRESS
        street = soup_inner_page.find(name=STREET_ELEMENT, class_=STREET_ELEMENT_CLASS).getText()

        # FOR THE CITY ELEMENT HAD TO REMOVE THE SUBSTRING 'location_on' TO CLEAN THE DATA
        city = soup_inner_page.select(f".{CITY_ELEMENT_CLASS} {CITY_ELEMENT}")[0].getText()
        city = city.replace("location_on", "")

        address = f"{street} {city}"
        price = soup_inner_page.find(name=PRICE_ELEMENT, class_=PRICE_ELEMENT_CLASS).getText()

        search_object["publish_dates"].append(date)
        search_object["addresses"].append(address)
        search_object["prices"].append(price)
        search_object["links"].append(link)

    # SELECTOR FOR THE NEXT PAGES IS AN ID, DOUBLE CHECK IF IT'S AN ID OR A CLASS AND CHANGE ACCORDINGLY
    subsequent_page = soup.find(name="a", id=NEXT_PAGE_SELECTOR)
    search_object["next_page"] = f"{DOMAIN_URL}{subsequent_page.get('href')}"


def main():
    searched_page = MAIN_SEARCHED_WEBSITE
    first_called = True

    for i in range(5):
        print(searched_page)
        search_results = {
            "publish_dates": [],
            "addresses": [],
            "prices": [],
            "links": [],
        }
        if first_called:
            crawler(searched_page, search_results)
            first_called = False

        elif not first_called:
            searched_page = search_results["next_page"]
            crawler(searched_page, search_results)

        # fill_form(search_results)


# main()
searching_results = {
    "publish_dates": [],
    "addresses": [],
    "prices": [],
    "links": [],
    "next_page": ""
}
crawler(MAIN_SEARCHED_WEBSITE, searching_results)

print(searching_results)
