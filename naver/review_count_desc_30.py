import csv
import time
from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# CSV 파일 설정 및 기존 리뷰 불러오기
csv_file_path = 'top_30_reviews.csv'
try:
  with open(csv_file_path, mode='r', newline='', encoding='utf-8') as review_csv_file:
    existing_reviews = {rows[0]: int(rows[1]) for rows in csv.reader(review_csv_file) if rows}
except FileNotFoundError:
  existing_reviews = {}

# Selenium WebDriver 설정
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--remote-allow-origins=*")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://map.naver.com/p/search/%EC%84%B1%EA%B7%A0%EA%B4%80%EB%8C%80%EC%97%AD%20%EC%9D%8C%EC%8B%9D%EC%A0%90?c=15.00,0,0,0,dh"
driver.get(url)
time.sleep(6)

searchIFrame = driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe")
driver.switch_to.frame(searchIFrame)
time.sleep(1)

for p in range(4):  # 4페이지까지 순회
  scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.mFg6p")
  scroll_div = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div[1]")

  for _ in range(12):  # 더 많은 식당을 로드하기 위해 스크롤
    driver.execute_script("arguments[0].scrollBy(0,2000);", scroll_div)
    time.sleep(1)

  restaurant_names = driver.find_elements(By.XPATH, "//span[contains(@class, 'place_bluelink')]")

  for name in restaurant_names:
    name.click()
    time.sleep(1)

    driver.switch_to.default_content()
    time.sleep(10)
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, "iframe#entryIframe"))
    time.sleep(5)

    try:
      driver.execute_script("document.querySelector('a[href*=\"/review\"]').click();")  # 리뷰 클릭
      time.sleep(5)

      while True:
        more_details = driver.find_elements(By.CSS_SELECTOR, 'svg.EhXBV')
        if len(more_details) > 1:
          more_details[1].click()
          time.sleep(2)
        else:
          break

      review_contents = driver.find_elements(By.CSS_SELECTOR, 'li.MHaAm')
    except:
      review_contents = []

    # 리뷰 정보 추출 및 누적 합산
    for review_content in review_contents:
      review_name = review_content.find_element(By.CSS_SELECTOR, '.t3JSf').text.strip('"""').strip()  # 리뷰 내용
      try:
        review_count = int(review_content.find_element(By.CSS_SELECTOR, '.CUoLy').text.split("\n")[1])  # 리뷰 갯수
      except:
        review_count = -1

      if review_count >= 1:
        if review_name in existing_reviews:
          existing_reviews[review_name] += review_count
        else:
          existing_reviews[review_name] = review_count

        # 누적된 리뷰 내용을 CSV 파일에 즉시 기록
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as review_csv_file:
          review_csv_writer = csv.writer(review_csv_file)
          for r_name, r_count in existing_reviews.items():
            review_csv_writer.writerow([r_name, r_count])

    driver.switch_to.default_content()
    time.sleep(1)
    driver.switch_to.frame(searchIFrame)
    time.sleep(1)

  try:
    next_page = driver.find_element(By.XPATH, "//a[.//span[contains(text(), '다음페이지')]]")
    next_page.click()
    time.sleep(2)
  except:
    break

# 정리 작업
driver.quit()
