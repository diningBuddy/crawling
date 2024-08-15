import pandas as pd

# CSV 파일을 읽어옵니다.
data = pd.read_csv('kakao_restaurants.csv')

# DataFrame을 JSON 형식으로 변환합니다.
data_json = data.to_json(orient='records', force_ascii=False, indent=4)

# JSON 데이터를 파일로 저장합니다.
with open('kakao_restaurants.json', 'w', encoding='utf-8') as f:
  f.write(data_json)

print("JSON 파일이 생성되었습니다.")
