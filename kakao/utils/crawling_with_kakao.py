import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

csv_file = open('../data/kakao_restaurants.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'name', 'category','review_count','address','rating','rating_count', 'phone_number', 'operate_time','url'])

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

inputBox = driver.find_element(By.CSS_SELECTOR, "input[id='search.keyword.query']")
search_keyword = "성균관대역 음식점"
inputBox.send_keys(search_keyword)
search_button = driver.find_element(By.CSS_SELECTOR, "button[id='search.keyword.submit']")
driver.execute_script("arguments[0].click();", search_button)
time.sleep(1)

more_button = driver.find_element(By.ID, "info.search.place.more")
if more_button.is_displayed() and 'HIDDEN' not in more_button.get_attribute('class'):
    driver.execute_script("arguments[0].click();", more_button)

move_first_page = driver.find_element(By.CSS_SELECTOR, "a[id='info.search.page.no1']")
driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", move_first_page)
driver.execute_script("arguments[0].click();", move_first_page)

time.sleep(6)
id = 1
for i in range(7):
    for p in range(5):  # 5페이지까지

        restaurant_names = set()
        restaurant_categories = set()

        review_rating = set()
        reviews = set()
        rating_count=set()
        # 요소를 스크롤할 때의 높이 설정

        restaurant_names = driver.find_elements(By.XPATH, "//a[contains(@class, 'link_name')]")
        restaurant_categories = driver.find_elements(By.XPATH,
                                                     "//div[@class='head_item clickArea']//span[@class='subcategory clickable']")
        review_count = driver.find_elements(By.XPATH, "//em[contains(@data-id, 'numberofreview')]")
        address = driver.find_elements(By.XPATH, "//p[contains(@data-id, 'address')]")
        review_rating = driver.find_elements(By.XPATH, "//em[contains(@data-id, 'scoreNum')]")
        rating_count = driver.find_elements(By.XPATH, "//a[contains(@data-id, 'numberofscore')]")

        phone_number = driver.find_elements(By.XPATH, "//span[contains(@data-id, 'phone')]")
        periodTxt = driver.find_elements(By.XPATH, "//a[contains(@data-id, 'periodTxt')]")

        more_review_buttons = driver.find_elements(By.CSS_SELECTOR, "a.moreview")

        hrefs = [button.get_attribute('href') for button in more_review_buttons]
        time.sleep(2)

        for h in hrefs:
            rating_count_text = rating_count[(id-1)%15].text.replace('건', '').strip()
            csv_writer.writerow([id, restaurant_names[(id - 1)%15].text, restaurant_categories[(id - 1)%15].text,
                                 review_count[(id-1)%15].text, address[(id-1)%15].text, review_rating[(id - 1)%15].text, rating_count_text
                                 , phone_number[(id-1)%15].text, periodTxt[(id-1)%15].text, h])
            id += 1

        if p == 4:
            next_chapter = driver.find_element(By.ID, "info.search.page.next")
            driver.execute_script("arguments[0].click();", next_chapter)
            time.sleep(2)
            break

        next_page_button = driver.find_element(By.CSS_SELECTOR, f"#info\\.search\\.page\\.no{(p+2)}")
        driver.execute_script("arguments[0].click();", next_page_button)

        time.sleep(2)

csv_file.close()
kakao_url_csv_file.close()




