## Kakao Crawling 프로세스
### 1. kakao_restaurants.py 실행

kakao_restaurants.py 스크립트를 실행하여 식당 정보를 수집합니다.

### 2. 검색되지 못한 식당 재검색

검색되지 못한 식당은 re_search.py를 통해 재검색됩니다.
재검색 결과는 missing_restaurant_names.txt 파일에 저장됩니다.

### 3. 추가 검색 및 중복 병합

그럼에도 검색되지 않은 식당은 missing_restaurant_update.py를 통해 재검색합니다.
중복 데이터가 존재할 수 있으므로 병합 과정을 거칩니다.
최종적으로 api_detail에 사용할 restaurant.csv 파일과 not_found_restaurants.txt 파일이 생성됩니다.

### 4. 메뉴 데이터 적재

kakao_menus.py를 실행하여 메뉴 데이터를 적재합니다.

디렉토리 구조
~~~
kakao/
│
├── core/
│   └── ...  # kakao_crawling 관련 내용
│
├── data/
│   └── ...  # kakao_crawling 관련 내용에 대한 Data
│
└── menus/
    └── ...  # kakao_menus 검색 및 반환 Data 보관
~~~