import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load kakao_restaurants.csv
restaurants_df = pd.read_csv("kakao_restaurants.csv")
restaurant_names = restaurants_df['name'].tolist()  # Extract the restaurant names

# Configure Selenium WebDriver
options = Options()
options.add_argument("--headless")  # Run in headless mode for automation
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Access the URL (율전동에 대한 내용)
url = "https://app.map.kakao.com/rank/places/search.json?appVersion=5.18.1&category-or-menu=category_all&deviceModel=iPhone%2014%20Pro&lang=ko&limit=100&osVersion=17.5.1&pf=iOS&region=B22880600&serviceName=kakaomap&type=search"
driver.get(url)

# Retrieve the JSON data (this part may vary depending on how the data is loaded in the actual page)
pre = driver.find_element(By.TAG_NAME, "pre").text  # Assuming the JSON data is in a <pre> tag
data = json.loads(pre)

# Close the WebDriver
driver.quit()

# Parse JSON data
items = data['items']
parsed_data = []
index = 1  # Initialize the rank index starting from 1

# Iterate over the JSON data and only add the restaurants present in kakao_restaurants.csv
for item in items:
  restaurant_name = item.get("name")

  # Only include the restaurant if its name is in the kakao_restaurants.csv list
  if restaurant_name in restaurant_names:
    parsed_data.append({
      "rank": index,  # Use the index variable as rank
      "name": restaurant_name,
      "lat": item.get("lat"),
      "lon": item.get("lon"),
      "category_name": item.get("category_name"),
      "review_count": item.get("review_count"),
      "review_rating": item.get("review_rating"),
      "thumbnail": item.get("thumbnail"),
    })
    index += 1  # Increment the index for the next restaurant

# Create DataFrame
df = pd.DataFrame(parsed_data)

# Save to CSV
df.to_csv("kakao_map_ranks.csv", index=False, encoding="utf-8-sig")

print("CSV file has been created successfully.")