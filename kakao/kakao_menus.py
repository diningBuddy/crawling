import pandas as pd

# 파일 경로 설정
menus_file = '../naver/menus.csv'
not_found_file = 'not_found_restaurants.csv'
output_file = 'kakao_menus.csv'

# CSV 파일 읽기
menus_df = pd.read_csv(menus_file)
not_found_df = pd.read_csv(not_found_file, header=None, names=['id', 'name'])

# 'id' 열만 사용하여 제거할 항목의 ID 목록 생성
not_found_ids = not_found_df['id'].tolist()

# not_found_ids에 포함되지 않은 메뉴만 필터링
filtered_menus_df = menus_df[~menus_df['restaurant_id'].isin(not_found_ids)]

# 결과를 새로운 CSV 파일로 저장
filtered_menus_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Filtering complete. The filtered data has been saved to {output_file}.")
