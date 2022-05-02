import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import utils
from db.Article import Article
from db.Keyword import Keyword
from sentence_rewriter import SentenceRewriter
import sys
from urllib.parse import urljoin, urlparse

from utils import give_emoji_free_text

"""
    Step1: Open the browser
    Step2: Search for the product 
    Step3: Extract the html content of all the products
    Step4: Extract the product description, price, ratings, reviews count and URL
    Step5: Record the product information in a product record list
    Step6: Repeat for all the pages
    Step7: Close the browser
    Step8: Write all the product's information in the product record list in the spreadsheet
"""

config = {
    'user': 'aaaccess_amazon',
    'password': 'gh05tCom!(($',
    'host': '209.145.58.115',
    'port': 3306,
    'database': 'aaaccess_amazon'
}

AMAZON_URL = "https://www.amazon.com"


class AmazonProductScraper:
    def __init__(self):
        self.driver = None
        self.category_name = None
        self.formatted_category_name = None
        self.article = Article(config)

    def open_browser(self):

        opt = Options()

        opt.add_argument("--disable-infobars")
        opt.add_argument("--disable-extensions")
        opt.add_argument('--log-level=OFF')
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opt)
        # Website URL
        self.driver.get(AMAZON_URL)

        # Wait till the page has been loaded
        time.sleep(3)

    def get_category_url(self, word):
        self.formatted_category_name = word.replace(" ", "+")
        # This is the product url format for all products
        category_url = AMAZON_URL + "/s?k={}&ref=nb_sb_noss"

        category_url = category_url.format(self.formatted_category_name)

        print(">> Category URL: ", category_url)

        # Go to the product webpage
        self.driver.get(category_url)
        # To be used later while navigating to different pages
        return category_url

    def extract_webpage_information(self):
        # Parsing through the webpage
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # List of all the html information related to the product
        page_results = soup.find_all('div', {'data-component-type': 's-search-result'})

        return page_results

    # @staticmethod
    def extract_product_information(self, page_results):
        temp_record = []
        for i in range(len(page_results)):
            item = page_results[i]

            # Find the a tag of the item
            a_tag_item = item.h2.a

            # Name of the item
            description = a_tag_item.text.strip()

            # Get the url of the item
            category_url = AMAZON_URL + a_tag_item.get('href')
            article_exists = self.article.article_exists(category_url);
            if article_exists:
                continue

            [product_future, evalu, product_url] = self.navigate_to_product_page(category_url)

            product_url = urljoin(product_url, urlparse(product_url).path)
            # Get the price of the product
            try:
                product_price_location = item.find('span', 'a-price')
                product_price = product_price_location.find('span', 'a-offscreen').text
            except AttributeError:
                # product_price = "N/A"
                continue

            try:
                product_img = item.find('img', 's-image').get('srcset')
                product_img = product_img.split(", ")[-1].split(" ")[0]
                print(product_img)
            except AttributeError:
                product_img = "N/A"

            # Get product reviews
            try:
                product_review = item.i.text.strip()
            except AttributeError:
                product_review = "N/A"

            # Get number of reviews
            try:
                review_number = item.find('span', {'class': 'a-size-base'}).text
            except AttributeError:
                review_number = "N/A"


            product = {
                "title": description,
                "price": product_price,
                "review": evalu,
                "review_number": evalu,
                "product_url": product_url,
                "product_image": product_img,
                "product_future": product_future

            }
            temp_record.append(product)
            if len(temp_record) == 10:
                break

        # if len(temp_record) < 10:
        #     res = self.extract_product_information()
        #     temp_record = temp_record + res

        return temp_record

    def close_browser(self):
        self.driver.close()

    def navigate_to_other_pages(self, category_url):
        # Contains the list of all the product's information
        records = []

        print("\n>> Page 1 - webpage information extracted")

        try:
            max_number_of_pages = "//span[@class='s-pagination-item s-pagination-disabled']"
            number_of_pages = self.driver.find_element_by_xpath(max_number_of_pages)
            print("Maximum Pages: ", number_of_pages.text)
        except NoSuchElementException:
            max_number_of_pages = "//li[@class='a-normal'][last()]"
            number_of_pages = self.driver.find_element_by_xpath(max_number_of_pages)

        for i in range(2, int(number_of_pages.text) + 1):
            # Goes to next page
            next_page_url = category_url + "&page=" + str(i)
            self.driver.get(next_page_url)

            # Webpage information is stored in page_results
            page_results = self.extract_webpage_information()
            temp_record = self.extract_product_information(page_results)

            extraction_information = ">> Page {} - webpage information extracted"
            print(extraction_information.format(i))

            for j in temp_record:
                records.append(j)

        self.driver.close()

        print("\n>> Creating an excel sheet and entering the details...")

        return records

    def product_information_to_database(self, records, keywordId):
        today = date.today().strftime("%d-%m-%Y")
        for record in records:
            record['keywordId'] = keywordId
            self.article.insert_articles(record)

    def navigate_to_product_page(self, product_url):
        page_url = product_url
        self.driver.get(page_url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        final_url = self.driver.current_url
        # List of all the html information related to the product
        page_results = soup.find_all('div', {'id': 'feature-bullets'})
        evalu = 0
        try:
            review = soup.find_all('span', {'data-hook': 'rating-out-of-text'})
            evaluate = review[0].text.split(" ")[0]
            evalu = int((float(evaluate) / 5) * 100)
        except:
            evalu = 85


        future_bullets = ''
        for el in page_results:
            futures = el.find_all('li', attrs={'class': None})
            for future in futures:
                text = future.span.text
                text = give_emoji_free_text(text)
                sentence_rewriter = SentenceRewriter()
                temp_ = sentence_rewriter.rewrite(text)

                future_bullets += (
                            "\u003ci class=\u0022vertmiddle mr10 rhicon rhi-check greencolor font130\u0022\u003e \u003c/i\u003e" + temp_ + "\u003cbr\u003e")
        print(future_bullets)
        return [future_bullets, evalu, final_url]


if __name__ == "__main__":
    my_amazon_bot = AmazonProductScraper()
    my_amazon_bot.open_browser()
    try:
        keyword = Keyword(config)
        keywords = keyword.select()
        for word in keywords:
            category_details = my_amazon_bot.get_category_url(word["keyword"])
            products = my_amazon_bot.extract_product_information(my_amazon_bot.extract_webpage_information())
            my_amazon_bot.product_information_to_database(products, word['id'])
            keyword.keyword_scraped(word["id"])
            # if word['scrapeEveryMonth'] == 1:
            #     next_date = utils.add_months(date.today(), 1)
            #     keyword.update_scrape_date(next_date, word['id'])



        my_amazon_bot.close_browser()
        sys.exit()
    except Exception as e:
        print(e.with_traceback())
        my_amazon_bot.close_browser()
        sys.exit()
