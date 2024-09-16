import pandas as pd
import re

# CSV 파일 읽기
kakao_restaurants_df = pd.read_csv('kakao_restaurants.csv')
naver_restaurants_df = pd.read_csv('../naver/restaurants.csv')

# 1번 파일(kakao_restaurants.csv)과 3번 파일(restaurants.csv)의 restaurant_id 비교
kakao_restaurant_ids = set(kakao_restaurants_df['id'])
restaurant_ids = set(naver_restaurants_df['id'])

# 1번 파일에 존재하지 않는 restaurant_id 찾기
missing_ids = restaurant_ids - kakao_restaurant_ids

# 해당 restaurant_id의 restaurant_name 추출
missing_restaurants = naver_restaurants_df[naver_restaurants_df['id'].isin(missing_ids)]

# 추출된 restaurant_name과 id를 이용해 검색
missing_names = missing_restaurants[['id', 'name']].values.tolist()

# 치환할 패턴 정의
replace_pattern = re.compile(r'(성대점|영통1호점|천천동점|성대역본점|성대역사점|수원성대역점|성균관대점|수원장안점|수원천천점|정자천천점|coffee&dessert|비건디저트|본점|천천점|율전점|수원|성균관대3호점|치킨포차 특제염지로 맛있는 치맥생각날때|X)')

# kakao_crawling.py에서 검색할 수 있도록 출력 및 저장
print("Kakao에서 검색할 restaurant_names:")
with open('missing_restaurant_names.txt', 'w', encoding='utf-8') as f:
  for restaurant_id, name in missing_names:
    # '성대점', '성대역본점', '성대역사점'등 치환
    modified_name = replace_pattern.sub('', name).strip()

    # 출력 및 파일에 기록 (ID 뒤에 콤마 제거)
    print(f"{restaurant_id}, {modified_name + ' 장안구'}")
    f.write(f"{restaurant_id} {modified_name + ' 장안구'}\n")

print("처리가 완료되었습니다. 'missing_restaurant_names.txt' 파일을 확인하세요.")
