from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time

CHROME_DRIVER_PATH = ""
MAIN_WEBSITE = ""
A_TAGS_CLASS = ""


def crawler(website_url, search_object):
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept-Language": "en-US,en;q=0.5"
    }

    response = requests.get(website_url, headers=header)

    data = response.text
    soup = BeautifulSoup(data, "html.parser")

    all_link_elements = soup.select(A_TAGS_CLASS)

    print(all_link_elements)


def main():
    searched_page = MAIN_WEBSITE
    first_called = True

    search_results = {
        "publish_dates": [],
        "addresses": [],
        "prices": [],
        "links": [],
        "next_page": ""
    }

    for i in range(10):
        if first_called:
            crawler(searched_page, search_results)
            first_called = False

        elif not first_called:
            searched_page = search_results["next_page"]
            search_results = {
                "publish_dates": [],
                "addresses": [],
                "prices": [],
                "links": [],
                "next_page": ""
            }
            crawler(searched_page, search_results)

        fill_form(search_results)


main()
