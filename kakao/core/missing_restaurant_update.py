import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# 기존 CSV 파일을 읽어서 데이터프레임으로 로드
if os.path.exists('../data/kakao_restaurants.csv'):
  existing_df = pd.read_csv('../data/kakao_restaurants.csv')
else:
  existing_df = pd.DataFrame(columns=['id', 'name', 'category', 'review_count', 'address', 'rating', 'rating_count', 'phone_number', 'operate_time', 'url'])

# 검색되지 않은 레스토랑을 저장할 CSV 파일 열기
not_found_file = open('../data/not_found_restaurants.txt', mode='w', encoding='utf-8')

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
with open('../data/missing_restaurant_names.txt', 'r', encoding='utf-8') as f:
  restaurant_names = f.read().splitlines()

# 크롤링된 데이터를 저장할 리스트
new_data = []

for line in restaurant_names:
  # 공백을 기준으로 분리하여 ID와 이름 부분을 추출
  id_part, name_part = line.split(' ', 1)

  # 이미 존재하는 ID인지 확인
  if int(id_part) in existing_df['id'].values:
    print(f"ID {id_part} already exists. Skipping update.")
    continue

  # Selenium을 사용하여 식당 이름 검색
  search_box.clear()
  search_box.send_keys(name_part)
  search_box.send_keys(Keys.RETURN)
  time.sleep(2)

  try:
    restaurant_name_element = driver.find_element(By.XPATH, "//a[contains(@class, 'link_name')]")
  except:
    # 검색 결과가 없을 경우 not_found_restaurants.txt에 기록
    not_found_file.write(f"{id_part} {name_part}\n")
    print(f"ID {id_part} not found. Recorded in not_found_restaurants.txt.")
    continue  # 다음 루프로 넘어감

  # 정보 추출
  try:
    category_element = driver.find_element(By.XPATH, "//div[@class='head_item clickArea']//span[@class='subcategory clickable']")
    address_element = driver.find_element(By.XPATH, "//p[@data-id='address']")
    rating = driver.find_element(By.XPATH, "//em[contains(@data-id, 'scoreNum')]")
    rating_eval_count_element = driver.find_element(By.XPATH, "//a[contains(@data-id, 'numberofscore')]")
    number_of_review_element = driver.find_element(By.XPATH, "//em[contains(@data-id, 'numberofreview')]")
    phone_number_element = driver.find_element(By.XPATH, "//span[@data-id='phone']")
    operate_time_element = driver.find_element(By.XPATH, "//a[contains(@data-id, 'periodTxt')]")
    detail_link_element = driver.find_element(By.XPATH, "//a[@class='moreview']")
    detail_link = detail_link_element.get_attribute('href')

    # 평가 수 텍스트 처리
    rating_eval_count_element_text = ''
    if '건' in rating_eval_count_element.text:
      rating_eval_count_element_text = rating_eval_count_element.text.replace('건', '').strip()

    # '영업시간' 텍스트 제거
    operate_time_text = operate_time_element.text.replace('영업시간', '').strip()

    # 새로운 데이터 리스트에 추가, ID는 int형으로 처리하여 추가
    new_data.append([
      int(id_part),  # ID는 정수형으로 처리
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

  except Exception as e:
    print(f"Error while extracting data for ID {id_part}: {e}")
    not_found_file.write(f"{id_part} {name_part}\n")
    continue

  time.sleep(2)

# 새로운 데이터를 데이터프레임으로 변환
new_df = pd.DataFrame(new_data, columns=['id', 'name', 'category', 'review_count', 'address', 'rating', 'rating_count', 'phone_number', 'operate_time', 'url'])

# 기존 데이터프레임과 새로운 데이터프레임을 병합
updated_df = pd.concat([existing_df, new_df], ignore_index=True)

# ID 기준으로 오름차순 정렬
updated_df = updated_df.sort_values(by='id', ascending=True)

# 중복된 name과 address가 있는 경우 하위 id의 레코드를 제거
updated_df = updated_df.drop_duplicates(subset=['name', 'address'], keep='first')

# CSV 파일에 저장 (기존 데이터를 덮어쓰지 않도록)
updated_df.to_csv('kakao_restaurants.csv', index=False, encoding='utf-8-sig')

# CSV 파일 닫기
not_found_file.close()

# Selenium 드라이버 종료
driver.quit()

print("크롤링 완료 및 CSV 파일 업데이트가 완료되었습니다.")
