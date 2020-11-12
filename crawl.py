import requests
import json
import time
import ast
import random
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm


def crawl_arxiv_by_month(year, month, save=True):
    url = f"https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-computer_science=y&classification-physics_archives=all&classification-include_cross_list=include&date-year=&date-filter_by=date_range&date-from_date={year}-{month}&date-to_date={year}-{month}&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first"
    driver_path = r"./chromedriver.exe"
    chr_options = Options()
    chr_options.add_experimental_option("detach", True)
    # chr_options.add_argument('headless')
    driver = webdriver.Chrome(driver_path, options=chr_options)
    driver.get(url)
    lst = []
    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        block = soup.find("ol", attrs={"class": "breathe-horizontal"})
        papers = block.find_all("li", attrs={"class": "arxiv-result"})
        for paper in papers:
            title = paper.find("p", attrs={"class": "title is-5 mathjax"}).text.strip()
            link = paper.find("div", attrs={"class": "is-marginless"}).find("a").get("href")
            abstract = paper.find("span", attrs={"class": "abstract-short"}).text.replace("▽ More", "").strip()
            date = paper.find("p", attrs={"class": "is-size-7"}).find_all(text=True)[1].strip().replace(";", "")
            tags = paper.find("div", attrs={"class": "tags is-inline-block"}).find_all(text=True)
            tags = [tag for tag in tags if tag != "\n"]
            authors = paper.find("p", attrs={"class": "authors"}).find_all(text=True)[2:]
            authors = [author.replace(",", "").strip() for author in authors]
            authors = [str(author) for author in authors if len(author) != 0]
            lst.append([title, authors, link, abstract, date, tags])
        try: 
            time.sleep(1)
            driver.find_element_by_class_name("pagination-next").click()
        except : 
            break
    driver.quit()
    data = pd.DataFrame(lst, columns=["title", "authors", "link", "abstract", "date", "tags"])
    data = dataframe_preprocessing(data)
    if save:
        data.to_csv(f"./data/arxiv_y{year}_m{month}.csv", index=False)
    return data


def dataframe_preprocessing(data):
    data.loc[:, "date"] = pd.to_datetime(data.loc[:, "date"])
    data.loc[:, "date"] = data.loc[:, "date"].apply(lambda x: x.date())
    data.loc[:, "authors"] = data.loc[:, "authors"].apply(str)
    data.loc[:, "authors"] = data.loc[:, "authors"].apply(perfect_eval)
    data.loc[:, "tags"] = data.loc[:, "tags"].apply(str)
    data.loc[:, "tags"] = data.loc[:, "tags"].apply(perfect_eval)
    data.loc[:, "link"] = data.loc[:, "link"].apply(lambda x: x.replace("abs", "pdf"))
    return data


def perfect_eval(anonstring):
    try:
        ev = ast.literal_eval(anonstring)
        return ev
    except ValueError:
        corrected = "\'" + anonstring + "\'"
        ev = ast.literal_eval(corrected)
        return ev


def crawl():
    for month in tqdm(range(1, 12)):
        data = crawl_arxiv_by_month(year=2020, month=month)


def main():
    crawl()


if __name__ == "__main__":
    main()