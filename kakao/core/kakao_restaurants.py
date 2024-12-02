import csv
import time
import os
import pandas as pd


import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# CSV 파일 설정
csv_file = open('../data/kakao_restaurants.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'name', 'category', 'review_count', 'address', 'rating', 'rating_count', 'phone_number', 'operate_time', 'url'])

# 카테고리 저장을 위한 set
categories_set = set()

# Selenium WebDriver 설정
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
user_agent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
options.add_argument(user_agent)
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--remote-allow-origins=*")

# 크롬 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# 카카오맵 접속
url = "https://map.kakao.com/"
driver.get(url)
time.sleep(6)

# 검색어 입력 및 검색 실행
search_box = driver.find_element(By.CSS_SELECTOR, "input[id='search.keyword.query']")
search_keyword = "성균관대역 음식점"
search_box.send_keys(search_keyword)
search_button = driver.find_element(By.CSS_SELECTOR, "button[id='search.keyword.submit']")
driver.execute_script("arguments[0].click();", search_button)
time.sleep(1)

# 위치 고정
location_fix = driver.find_element(By.CSS_SELECTOR, "span[id='search.keyword.currentmap']")
driver.execute_script("arguments[0].click();", location_fix)

# 기존 CSV 파일에서 식당 이름 목록 가져오기
naver_map_crawling_path = '../../naver/restaurants.csv'
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
    id += 1
    continue

  # 정보 추출
  category_element = driver.find_element(By.XPATH, "//div[@class='head_item clickArea']//span[@class='subcategory clickable']")
  address_element = driver.find_element(By.XPATH, "//p[@data-id='address']")
  rating = driver.find_element(By.XPATH, "//em[contains(@data-id, 'scoreNum')]")
  rating_eval_count_element = driver.find_element(By.XPATH, "//a[contains(@data-id, 'numberofscore')]")
  number_of_review_element = driver.find_element(By.XPATH, "//em[contains(@data-id, 'numberofreview')]")
  phone_number_element = driver.find_element(By.XPATH, "//span[@data-id='phone']")
  operate_time_element = driver.find_element(By.XPATH, "//a[contains(@data-id, 'periodTxt')]")
  detail_link_element = driver.find_element(By.XPATH, "//a[@class='moreview']")
  detail_link = detail_link_element.get_attribute('href')

  # 카테고리 저장
  categories_set.add(category_element.text)

  # 평가 수 텍스트 처리
  rating_eval_count_element_text = ''
  if '건' in rating_eval_count_element.text:
    rating_eval_count_element_text = rating_eval_count_element.text.replace('건', '').strip()

  # '영업시간' 텍스트 제거
  operate_time_text = operate_time_element.text.replace('영업시간', '').strip()

  # CSV 파일에 쓰기
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

# kakao_map_ranks.csv 파일이 존재하면 추가적으로 처리
kakao_map_ranks_path = '../kakao_map_ranks.csv'
if os.path.exists(kakao_map_ranks_path):
  kakao_restaurants_df = pd.read_csv(kakao_map_ranks_path)
  kakao_restaurant_names = kakao_restaurants_df['name'].tolist()

  for name in kakao_restaurant_names:
    search_box.clear()
    search_box.send_keys(name)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)

    try:
      restaurant_name_element = driver.find_element(By.XPATH, "//a[contains(@class, 'link_name')]")
    except:
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

    # 카테고리 저장
    categories_set.add(category_element.text)

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

# CSV 파일 정리 및 중복 제거
csv_file.close()

df = pd.read_csv('../data/kakao_restaurants.csv')
df.drop_duplicates(subset=['name', 'address'], keep='first', inplace=True)
df.to_csv('../data/kakao_restaurants.csv', index=False, encoding='utf-8-sig')

# 카테고리 set을 텍스트 파일로 저장
with open('../data/kakao_categories.txt', 'w', encoding='utf-8') as f:
  for category in sorted(categories_set):
    f.write(f"{category}\n")

# Selenium 드라이버 종료
driver.quit()

print("크롤링 완료 및 중복 데이터 제거가 완료되었습니다.")
