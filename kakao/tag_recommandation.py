import openai
import pandas as pd
from dotenv import load_dotenv
import os

# .env 파일에서 API 키 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# CSV 파일에서 식당 정보 로드
df = pd.read_csv('../naver/review_csv_file.csv')  # 여기에 실제 CSV 파일 경로

# 네이버 방문 리뷰 상위 20개 (식당별로 그룹화하고, 리뷰 내용과 리뷰 수를 함께 리스트로 만듦)
reviews = df.groupby('restaurant_id').apply(lambda x: list(zip(x['review_name'], x['review_count'])))

# 태그 매칭을 위한 함수 (리뷰 가중치를 종합)
def get_tags_for_restaurant(restaurant_name, restaurant_reviews):
  # 리뷰 내용을 가중치(리뷰 수)와 함께 출력
  reviews_text = "\n".join([f"- {review_name} (리뷰 수: {review_count})" for review_name, review_count in restaurant_reviews])
  prompt = f"""
    다음은 "{restaurant_name}"에 대한 리뷰 목록과 각 리뷰의 추천 수입니다:
    
    {reviews_text}

    각 리뷰의 추천 수(review_count)가 높을수록, 그 리뷰의 중요도를 높게 평가하세요. 추천 수가 많으면 그 내용이 다른 리뷰보다 더 중요하게 고려되어야 합니다.

    위 리뷰들을 종합하여, 아래의 태그 그룹에서 각 그룹당 가장 적합한 하나의 태그를 선택하세요. 각 그룹에서 가장 자주 언급되거나 중요하다고 판단되는 요소를 반영하여 결정해 주세요.
    
    목적: '데이트', '단체모임', '기념일'
    분위기: '조용한', '편한좌석'
    테마: '인테리어', '특별한메뉴', '사진맛집', '뷰맛집', '신선한', '다양한술', '이국적인', '가성비', '직접 구워주는'
    시설: '룸', '연인석', '루프탑', '1인석', '놀이방', '유아의자', '넓은'
    
    리뷰 내용과 추천 수에 따라, 각 그룹에서 가장 적합한 태그 하나를 반환하세요:
    
    목적: 
    분위기: 
    테마: 
    시설: 
    
    다른 이야기는 다 빼고 음식점 이름을 기반으로 리스트로 알려줘
    """

  response = openai.ChatCompletion.create(
      model="gpt-4-turbo",
      messages=[
        {"role": "system", "content": "당신은 태그 추천 전문가입니다."},
        {"role": "user", "content": prompt}
      ],
      max_tokens=200
  )

  # 태그 정보를 반환 (목적, 분위기, 테마, 시설을 분리)
  return response.choices[0].message['content'].strip()

# 데이터프레임에 태그 추가 (식당별 태그를 한 번만 추가)
def add_tags_to_dataframe(df, reviews):
  # 태그 데이터를 저장할 리스트
  tag_data = []

  for restaurant_id, restaurant_reviews in reviews.items():
    # 각 식당의 리뷰 20개를 종합하여 GPT API로 태그 추출 (리뷰 수를 함께 고려)
    tags = get_tags_for_restaurant(restaurant_id, restaurant_reviews[:20])  # 최대 20개의 리뷰만 사용

    # 태그를 각 그룹(목적, 분위기, 테마, 시설)으로 분리
    tag_lines = tags.split('\n')
    tag_dict = {
      'restaurant_id': restaurant_id,
      '목적': tag_lines[0].split(': ')[1] if len(tag_lines) > 0 else '',
      '분위기': tag_lines[1].split(': ')[1] if len(tag_lines) > 1 else '',
      '테마': tag_lines[2].split(': ')[1] if len(tag_lines) > 2 else '',
      '시설': tag_lines[3].split(': ')[1] if len(tag_lines) > 3 else ''
    }

    # 식당별로 한 번만 태그를 추가
    tag_data.append(tag_dict)
    print(f"식당: {restaurant_id} => 태그: {tags}")

  # 태그 데이터를 데이터프레임으로 변환
  tag_df = pd.DataFrame(tag_data)

  # 식당 ID로 기존 데이터프레임과 병합
  df_with_tags = pd.merge(df[['restaurant_id']].drop_duplicates(), tag_df, on='restaurant_id', how='left')
  return df_with_tags

# 태그가 추가된 데이터프레임 생성
df_with_tags = add_tags_to_dataframe(df, reviews)

# 결과를 CSV 파일로 저장 (각 식당에 대해 한 번만 태그가 기록됨)
df_with_tags.to_csv('data/restaurant_with_tags.csv', index=False)

print("태그 추천이 완료되고 결과가 저장되었습니다.")
