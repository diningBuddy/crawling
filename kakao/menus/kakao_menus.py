import pandas as pd

# 파일 경로 설정
menus_file = '../naver/menus.csv'
not_found_file = './data/not_found_restaurants.txt'
output_file = './menus/kakao_menus.csv'

# 파일 읽기
menus_df = pd.read_csv(menus_file)
not_found_df = pd.read_csv(not_found_file, header=None, names=['id', 'name'])

# not_found_file 읽을 때 수정
# 공백으로 구분된 첫 번째 값만 ID로 추출
with open(not_found_file, 'r', encoding='utf-8') as f:
  lines = f.readlines()
  not_found_ids = [line.strip().split()[0] for line in lines]

# 데이터 타입 통일
menus_df['restaurant_id'] = menus_df['restaurant_id'].astype(str)
not_found_ids = [str(id) for id in not_found_ids]

# 필터링
filtered_menus_df = menus_df[~menus_df['restaurant_id'].isin(not_found_ids)]

# 결과 확인
print("필터링 전 레코드 수:", len(menus_df))
print("제외할 ID 수:", len(not_found_ids))
print("필터링 후 레코드 수:", len(filtered_menus_df))
print("제외된 레코드 수:", len(menus_df) - len(filtered_menus_df))

# 결과 저장
filtered_menus_df.to_csv(output_file, index=False, encoding='utf-8-sig')
