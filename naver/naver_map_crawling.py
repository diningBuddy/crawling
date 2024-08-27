import csv
import time
from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

csv_file = open('restaurants.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'name', 'category', 'review_count', 'address', 'rating', 'number', 'image_url'])

menu_csv_file = open('menus.csv', mode='w', newline='', encoding='utf-8')
menu_csv_writer = csv.writer(menu_csv_file)
menu_csv_writer.writerow(['restaurant_id', 'menu_name', 'price', 'description', 'is_representative', 'image_url'])

operation_csv_file = open('operations.csv', mode='w', newline='', encoding='utf-8')
operation_csv_writer = csv.writer(operation_csv_file)
operation_csv_writer.writerow(['restaurant_id', 'restaurant_name', 'day', 'info'])

review_csv_file = open('review_csv_file.csv', mode='w', newline='', encoding='utf-8')
review_csv_writer = csv.writer(review_csv_file)
review_csv_writer.writerow(['restaurant_id', 'review_name', 'review_count'])

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

user_agent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
options.add_argument(user_agent)

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

restaurant_id = 1
for p in range(4):  # 4페이지까지
    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.mFg6p")

    scroll_div = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div[1]")
    restaurant_names = set()
    restaurant_categories = set()
    reviews = set()
    for _ in range(12):
        driver.execute_script("arguments[0].scrollBy(0,2000);", scroll_div)
        time.sleep(1)

    restaurant_names = driver.find_elements(By.XPATH, "//span[contains(@class, 'place_bluelink')]")
    restaurant_categories = driver.find_elements(By.XPATH, "//div[@class='N_KDL']//span[@class='KCMnt']")
    reviews = driver.find_elements(By.XPATH, "//div[contains(@class, 'Dr_06')]//span[@class='h69bs']")

    print(len(restaurant_names), len(restaurant_categories), len(reviews))

    for i, name in enumerate(restaurant_names):
        review = reviews[i].text.replace("리뷰 ", "")
        category = restaurant_categories[i].text.replace("\"", "")
        name_text = name.text
        print(i, name_text, category, review)

        name.click()
        time.sleep(1)

        driver.switch_to.default_content()
        time.sleep(1)
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, "iframe#entryIframe"))
        time.sleep(1.5)

        try:
            driver.find_element(By.CLASS_NAME, "_UCia").click()  # 주소 자세히 클릭
            time.sleep(1)

            address = driver.find_element(By.CLASS_NAME, "nQ7Lh").text
            address = address.replace("복사", "")
            address = address.replace("도로명", "")
            print(address)
        except:
            address = ""

        try:
            rating = driver.find_element(By.CLASS_NAME, "LXIwF").text.split("\n")[1]
        except:
            rating = ""

        try:
            number = driver.find_element(By.CLASS_NAME, "xlx7Q").text
        except:
            number = ""

        try:
            style_attribute = driver.find_element(By.XPATH, "//div[contains(@class, 'K0PDV')]").get_attribute('style')
            restaurant_image_url = unquote(style_attribute.split('url("')[1].split('")')[0])
        except Exception as e:
            print(e, "이미지 없음")
            restaurant_image_url = ""

        print(rating, number, restaurant_image_url)

        try:
            driver.find_element(By.CLASS_NAME, 'nmfMK').click()
            time.sleep(1)
        except:
            print()

        try:
            driver.find_element(By.CSS_SELECTOR, 'a.gKP9i.RMgN0').click()  # 영업 정보 클릭
            time.sleep(2)

            hours_info_elements = driver.find_elements(By.CSS_SELECTOR, 'div.w9QyJ > div.y6tNq > span.A_cdD')

            # 영업 시간 정보 추출 및 CSV 파일에 쓰기
            for info in hours_info_elements:
                text = info.text
                lines = text.split("\n")
                day = lines[0]
                info_text = "\n".join(lines[1:])

                operation_csv_writer.writerow([restaurant_id, name_text, day, info_text])
        except:
            operation_csv_writer.writerow([restaurant_id, name_text, "", ""])

        try:
            driver.execute_script("document.querySelector('a[href*=\"/menu\"]').click();")  # 메뉴 클릭
            time.sleep(2)

            menu_items = driver.find_elements(By.CSS_SELECTOR, 'li.E2jtL')
        except:
            menu_items = []
        menus = []

        # 각 메뉴 요소에 대하여 정보 추출
        for item in menu_items:
            menu_name = item.find_element(By.CSS_SELECTOR, '.lPzHi').text  # 메뉴 이름
            try:
                menu_price = item.find_element(By.CSS_SELECTOR, '.GXS1X em').text  # 가격
            except:
                menu_price = "-1"
            try:
                menu_description = item.find_element(By.CSS_SELECTOR, '.kPogF').text  # 설명
            except:
                menu_description = "설명 없음"  # 설명이 없는 경우

            # 대표 여부 확인
            representative = "대표" if len(item.find_elements(By.CSS_SELECTOR, '.QM_zp .place_blind')) > 0 else "일반"

            # 이미지 URL 추출
            try:
                image_style = item.find_element(By.CSS_SELECTOR, '.K0PDV').get_attribute('style')
                image_url = unquote(image_style.split('url("')[1].split('")')[0])
            except:
                image_url = ""

            # 정보를 리스트에 저장
            menus.append({
                "메뉴 이름": menu_name,
                "가격": menu_price,
                "설명": menu_description,
                "대표 여부": representative,
                "이미지 URL": image_url,
            })
            print({
                "메뉴 이름": menu_name,
                "가격": menu_price,
                "설명": menu_description,
                "대표 여부": representative,
                "이미지 URL": image_url,
            })

        csv_writer.writerow([restaurant_id, name_text, category, review, address, rating, number, restaurant_image_url])

        for menu in menus:
            menu_csv_writer.writerow(
                [restaurant_id, menu["메뉴 이름"], menu["가격"], menu["설명"], menu["대표 여부"], menu["이미지 URL"]])

        try:
            driver.execute_script("document.querySelector('a[href*=\"/review\"]').click();")  # 리뷰 클릭
            time.sleep(5)

            more_details = driver.find_elements(By.CSS_SELECTOR, 'svg.EhXBV')
            more_details[1].click()

            time.sleep(2)
            review_contents = driver.find_elements(By.CSS_SELECTOR, 'li.MHaAm')
        except:
            review_contents = []
        visitor_reviews = []

        # 각 리뷰 요소에 대하여 정보 추출
        for review_content in review_contents:
            review_name = review_content.find_element(By.CSS_SELECTOR, '.t3JSf').text.strip('"""').strip()  # 리뷰 내용
            try:
                review_count = review_content.find_element(By.CSS_SELECTOR, '.CUoLy').text.split("\n")[1]  # 리뷰 갯수
            except:
                review_count = "-1"

            if int(review_count)>=50:
                # 정보를 리스트에 저장
                visitor_reviews.append({
                    "리뷰 내용": review_name,
                    "리뷰 갯수": review_count,
                })
                print({
                    "리뷰 내용": review_name,
                    "리뷰 갯수": review_count,
                })

        for visitor_review in visitor_reviews:
            review_csv_writer.writerow(
                [restaurant_id, visitor_review["리뷰 내용"], visitor_review["리뷰 갯수"]])

        driver.switch_to.default_content()
        time.sleep(1)
        driver.switch_to.frame(searchIFrame)
        time.sleep(1)

        restaurant_id += 1

    driver.find_element(By.XPATH, "//a[.//span[contains(text(), '다음페이지')]]").click()

    time.sleep(2)

csv_file.close()
menu_csv_file.close()
operation_csv_file.close()
