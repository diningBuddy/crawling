import csv
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

csv_file = open('kakao_restaurants.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'name', 'category', 'review_count', 'address', 'rating', 'rating_count', 'phone_number', 'operate_time', 'url'])

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

user_agent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
options.add_argument(user_agent)

options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--remote-allow-origins=*")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://map.kakao.com/"
driver.get(url)
time.sleep(6)

search_box = driver.find_element(By.CSS_SELECTOR, "input[id='search.keyword.query']")
search_keyword = "성균관대역 음식점"
search_box.send_keys(search_keyword)
search_button = driver.find_element(By.CSS_SELECTOR, "button[id='search.keyword.submit']")
driver.execute_script("arguments[0].click();", search_button)
time.sleep(1)

location_fix = driver.find_element(By.CSS_SELECTOR, "span[id='search.keyword.currentmap']")
driver.execute_script("arguments[0].click();", location_fix)

naver_map_crawling_path = '../naver/restaurants.csv'
restaurants_df = pd.read_csv(naver_map_crawling_path)

restaurant_names = restaurants_df['name'].tolist()

id = 1
for name in restaurant_names:
  search_box.clear()
  search_box.send_keys(name)
  search_box.send_keys(Keys.RETURN)
  time.sleep(2)

  try:
    restaurant_name_element = driver.find_element(By.XPATH, "//a[contains(@class, 'link_name')]")
  except:
    restaurant_name = ''
    id += 1
    continue

  category_element = driver.find_element(By.XPATH, "//div[@class='head_item clickArea']//span[@class='subcategory clickable']")
  address_element = driver.find_element(By.XPATH, "//p[@data-id='address']")
  rating = driver.find_element(By.XPATH, "//em[contains(@data-id, 'scoreNum')]")
  rating_eval_count_element = driver.find_element(By.XPATH, "//a[contains(@data-id, 'numberofscore')]")
  number_of_review_element = driver.find_element(By.XPATH, "//em[contains(@data-id, 'numberofreview')]")
  phone_number_element = driver.find_element(By.XPATH, "//span[@data-id='phone']")
  operate_time_element = driver.find_element(By.XPATH, "//a[contains(@data-id, 'periodTxt')]")
  detail_link_element = driver.find_element(By.XPATH, "//a[@class='moreview']")
  detail_link = detail_link_element.get_attribute('href')

  rating_eval_count_element_text = ''
  if '건' in rating_eval_count_element.text:
    rating_eval_count_element_text = rating_eval_count_element.text.replace('건', '').strip()

  operate_time_text = operate_time_element.text

  csv_writer.writerow([
    id,
    restaurant_name_element.text,
    category_element.text,
    number_of_review_element.text,
    address_element.text,
    rating.text,
    rating_eval_count_element_text,
    phone_number_element.text,
    operate_time_text,
   detail_link,
  ])
  id += 1

  time.sleep(2)

csv_file.close()
