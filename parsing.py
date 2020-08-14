import sys
import time
from sqlite3 import IntegrityError

import mysql.connector
from bs4 import BeautifulSoup as BS
from mysql.connector import errorcode
from selenium import webdriver

filename = "info"
host = "https://olimpiada.ru"
# math_url = "https://olimpiada.ru/activities?type=ind&subject%5B6%5D=on&class=11&period_date=&period=year"
# info_url = "https://olimpiada.ru/activities?type=ind&subject%5B7%5D=on&class=11&period_date=&period=year"
url = "https://olimpiada.ru/activities?type=ind&subject%5B7%5D=on&class=11&period_date=&period=year"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 OPR/70.0.3728.95",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}

# Connecting to a database
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="kvant"

    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
        sys.exit()
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
        sys.exit()
    else:
        print(err)
        sys.exit()

cursor = db.cursor()


def add(items):
    for item in items:
        try:
            sql = """INSERT INTO `info`(`title`, `description`, `link`, `rating`) VALUES (%s,%s,%s,%s)"""
            val = item["title"], item["desk"], host+item["link"], item["rating"].replace(",", ".")
            cursor.execute(sql, val)
            db.commit()
        except IntegrityError:
            pass


# get html from site
def get_html(url):
    # req = Request(url, headers={'User-Agent' : 'Mozilla/5.0'})
    # response = urlopen(req).read()
    driver = webdriver.Chrome(executable_path="C:\webdrivers\operadriver.exe")
    driver.get(url)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return driver.page_source


# parsing
def get_content(html):
    soup = BS(html, "html.parser")
    articles = []
    items = soup.find_all("table")

    for item in items:
        try:
            title = item.find("span", class_="headline").get_text()
            desk = item.find("span", class_="headline red", style="").get_text()
            link = item.find("a", class_="none_a black").get("href")
            rating = item.find("span", class_="pl_rating").get_text()
        except Exception:
            continue
        articles.append({

            "title": title,
            "desk": desk,
            "link": link,
            "rating": rating

        })
    return articles


# saving file
# def save_file(items, path=(filename + ".csv")):
#     with open(path, "w", newline="", encoding="utf16")as file:
#         writter = csv.writer(file, delimiter="\t")
#         writter.writerow(["title", "desk", "link", "rating"])
#         for item in items:
#             writter.writerow([item["title"], item["desk"], item["link"], item["rating"]])

# main algorithm


def main():
    all_content = get_content(get_html(url))
    add(all_content)


if __name__ == '__main__':
    main()
