import time
import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Function to fetch JSON data from the provided URL
def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for URL {url} with status code {response.status_code}")
        return None

def get_kakao_coordinates(address: str, api_key: str) -> tuple:
    """
    카카오 REST API를 통해 주소의 위경도 좌표를 반환
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()["documents"][0]
            return float(result["y"]), float(result["x"])  # latitude, longitude
        return None, None
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None, None

def extract_coordinates(data):
    load_dotenv()
    api_key = os.getenv('KAKAO_REST_API_KEY')
    coordinates = {
        'latitude': None,
        'longitude': None
    }

    try:
        address_info = data.get('basicInfo', {}).get('address', {})
        if address_info:
            region = address_info.get('region', {})
            new_addr = address_info.get('newaddr', {})

            # 전체 주소 조합 (도로명 + 지역)
            full_address = f"{region.get('newaddrfullname', '')} {new_addr.get('newaddrfull', '')}"
            print(f"Querying address: {full_address}")

            if full_address.strip():
                lat, lon = get_kakao_coordinates(full_address, api_key)
                coordinates['latitude'] = lat
                coordinates['longitude'] = lon
    except Exception as e:
        print(f"Error extracting coordinates: {e}")

    return coordinates

# Function to extract operationInfo data
def extract_operation_info(data):
    operation_info = {
        'appointment': '',
        'delivery': '',
        'package': ''
    }
    try:
        op_info = data.get('basicInfo', {}).get('operationInfo', {})
        for key in operation_info.keys():
            operation_info[key] = 'Y' if key in op_info and op_info[key] else 'N'
    except Exception as e:
        print(f"Error extracting operationInfo: {e}")

    return operation_info

# Function to extract facilityInfo data
def extract_facility_info(data):
    facility_info = {
        'wifi': '',
        'pet': '',
        'parking': '',
        'nursery': '',
        'smokingroom': '',
        'fordisabled': ''
    }
    try:
        fac_info = data.get('basicInfo', {}).get('facilityInfo', {})
        for key in facility_info.keys():
            facility_info[key] = 'Y' if key in fac_info and fac_info[key] else 'N'
    except Exception as e:
        print(f"Error extracting facilityInfo: {e}")

    return facility_info

# Function to expand days in a day range to individual days
def expand_days(day_range):
    days = ['월', '화', '수', '목', '금', '토', '일']
    day_map = {'월': 0, '화': 1, '수': 2, '목': 3, '금': 4, '토': 5, '일': 6}
    if day_range == '매일':
        return days
    else:
        day_range_split = day_range.split('~')
        if len(day_range_split) == 2 and day_range_split[0] in day_map and day_range_split[1] in day_map:
            start_day, end_day = day_map[day_range_split[0]], day_map[day_range_split[1]]
            return days[start_day:end_day+1]
        else:
            return day_range.split(',')

# Function to generate operation_time JSON
def generate_operation_time(data):
    schedule = {day: {"시작시간": None, "종료시간": None, "휴게시작시간": None, "휴게종료시간": None, "라스트오더": None} for day in ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']}

    try:
        open_hour = data.get('basicInfo', {}).get('openHour', {})
        for period in open_hour.get('periodList', []):
            for time_info in period.get('timeList', []):
                days = expand_days(time_info.get('dayOfWeek', ''))
                time_name = time_info.get('timeName')
                time_range = time_info.get('timeSE', '').strip().split('~')

                for day in days:
                    day_name = day + "요일"
                    if time_name == '영업시간':
                        schedule[day_name]["시작시간"] = time_range[0].strip() if len(time_range) > 0 else None
                        schedule[day_name]["종료시간"] = time_range[1].strip() if len(time_range) > 1 else None
                    elif time_name == '라스트오더':
                        schedule[day_name]["라스트오더"] = time_range[1].strip() if len(time_range) > 1 else None
                    elif time_name == '휴게시간':
                        schedule[day_name]["휴게시작시간"] = time_range[0].strip() if len(time_range) > 0 else None
                        schedule[day_name]["휴게종료시간"] = time_range[1].strip() if len(time_range) > 1 else None
    except Exception as e:
        print(f"Error processing operation time: {e}")

    # Convert the dictionary to a properly formatted JSON string
    return json.dumps(schedule, ensure_ascii=False)  # No need to replace quotes

# Main function to process the DataFrame and generate JSON data for operation_time
def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Load the CSV file
    df = pd.read_csv('./data/kakao_restaurants.csv')

    # Process each row
    for idx, row in df.iterrows():
        url = row['url']
        if url == '':
            continue
        place_id = url.split('/')[-1]
        api_url = f'https://place.map.kakao.com/main/v/{place_id}'

        data = fetch_data(api_url, headers)
        if data:
            # Extract operationInfo and facilityInfo
            operation_data = extract_operation_info(data)
            facility_data = extract_facility_info(data)
            coordinate_data = extract_coordinates(data)

            # Update DataFrame with operationInfo and facilityInfo
            for key, value in operation_data.items():
                df.at[idx, key] = value
            for key, value in facility_data.items():
                df.at[idx, key] = value
            for key, value in coordinate_data.items():  # 추가된 부분
                df.at[idx, key] = value

            # Generate JSON string for operation_time
            operation_time_data = generate_operation_time(data)
            df.at[idx, 'operation_time'] = operation_time_data

            print(f"Updated row {idx+1}")

            time.sleep(0.1)

    # Drop the old columns related to last order as they are now included in operation_time
    columns_to_drop = ['매일_last_order', '월~토_last_order', '월~금_last_order', 'operate_time']
    df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

    # Save the updated DataFrame to a new CSV file
    df.to_csv('./data/kakao_restaurants.csv', index=False)

    print("Data extraction and CSV file creation complete.")

if __name__ == "__main__":
    main()
