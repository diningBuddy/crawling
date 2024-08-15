import time
import requests
import pandas as pd
import numpy as np

# Function to fetch JSON data from the provided URL
def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for URL {url} with status code {response.status_code}")
        return None

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
            if key in op_info:
                operation_info[key] = op_info[key]
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
            if key in fac_info:
                facility_info[key] = fac_info[key]
    except Exception as e:
        print(f"Error extracting facilityInfo: {e}")

    return facility_info

# Function to extract last order times
def extract_last_order_times(data):
    last_order_dict = {}
    try:
        open_hour = data.get('basicInfo', {}).get('openHour', {})
        for period in open_hour.get('periodList', []):
            for time in period.get('timeList', []):
                if time.get('timeName') == '라스트오더':
                    days = time.get('dayOfWeek', '').split(',')
                    last_order_time = time.get('timeSE', '').strip('~').strip()  # Extract the time only
                    for day in days:
                        last_order_dict[f"{day}_last_order"] = last_order_time
    except Exception as e:
        print(f"Error extracting last order times: {e}")
    return last_order_dict

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

# Main function to add new columns to the DataFrame and process time data
def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    df = pd.read_csv('kakao_restaurants.csv')

    # Add new columns for operationInfo, facilityInfo, and last order times
    operation_columns = ['appointment', 'delivery', 'package']
    facility_columns = ['wifi', 'pet', 'parking', 'nursery', 'smokingroom', 'fordisabled']
    last_order_columns = [f'{day}_last_order' for day in ['월', '화', '수', '목', '금', '토', '일']]
    days = ['월', '화', '수', '목', '금', '토', '일']

    for column in operation_columns + facility_columns + last_order_columns:
        if column not in df.columns:
            df[column] = ''

    # Add columns for opening and break times
    for day in days:
        df[f'{day}_start'] = np.nan
        df[f'{day}_end'] = np.nan
        df[f'{day}_break_start'] = np.nan
        df[f'{day}_break_end'] = np.nan

    # Process each row
    for idx, row in df.iterrows():
        url = row['url']
        if url == '':
            continue
        place_id = url.split('/')[-1]
        api_url = f'https://place.map.kakao.com/main/v/{place_id}'

        data = fetch_data(api_url, headers)
        if data:
            # Extract operationInfo, facilityInfo, and last order times
            operation_data = extract_operation_info(data)
            facility_data = extract_facility_info(data)
            last_order_data = extract_last_order_times(data)

            # Update DataFrame with the extracted data
            for key, value in operation_data.items():
                df.at[idx, key] = value

            for key, value in facility_data.items():
                df.at[idx, key] = value

            for key, value in last_order_data.items():
                df.at[idx, key] = value

            # Process operating and break times
            if pd.notnull(row['operate_time']):
                time_ranges = row['operate_time'].split('·')

                for time_range in time_ranges:
                    parts = time_range.strip().split(' ')

                    if "휴게시간" not in parts[0]:
                        # Process regular operating time
                        if len(parts) >= 4:
                            operate_start_time = parts[1]
                            operate_end_time = parts[3]
                            applicable_days = expand_days(parts[0])

                            for day in applicable_days:
                                df.at[idx, f'{day}_start'] = operate_start_time
                                df.at[idx, f'{day}_end'] = operate_end_time

                    else:
                        # Process break time
                        if len(parts) >= 5:
                            break_start_time = parts[2]
                            break_end_time = parts[4]
                            break_days = expand_days(parts[1])

                            for day in break_days:
                                df.at[idx, f'{day}_break_start'] = break_start_time
                                df.at[idx, f'{day}_break_end'] = break_end_time

            print(f"Updated row {idx+1}")

            time.sleep(0.1)

    # Save the updated DataFrame to a new CSV file
    df.to_csv('kakao_restaurants.csv', index=False)
    print("Data extraction and CSV file creation complete.")

if __name__ == "__main__":
    main()
