import pandas as pd
import json

# CSV 파일을 불러옵니다.
df = pd.read_csv('kakao_restaurants.csv')

# 각 요일의 컬럼명을 정의합니다.
days = ['월', '화', '수', '목', '금', '토', '일']

# JSON 변환을 위한 함수 정의
def generate_json(row):
  schedule = {}
  for day in days:
    schedule[day + "요일"] = {
      "시작시간": row[f"{day}_start"] if pd.notnull(row[f"{day}_start"]) else None,
      "종료시간": row[f"{day}_end"] if pd.notnull(row[f"{day}_end"]) else None,
      "휴게시작시간": row[f"{day}_break_start"] if pd.notnull(row[f"{day}_break_start"]) else None,
      "휴게종료시간": row[f"{day}_break_end"] if pd.notnull(row[f"{day}_break_end"]) else None,
      "라스트오더": row[f"{day}_last_order"] if pd.notnull(row[f"{day}_last_order"]) else None
    }
  return schedule

# 모든 레스토랑에 대해 JSON 생성
restaurants_json = {}

for index, row in df.iterrows():
  restaurant_name = row['name']
  restaurants_json[restaurant_name] = generate_json(row)

# JSON 파일로 저장
with open('restaurants_schedule.json', 'w', encoding='utf-8') as json_file:
  json.dump(restaurants_json, json_file, ensure_ascii=False, indent=4)

print("JSON 파일 생성 완료: restaurants_schedule.json")
