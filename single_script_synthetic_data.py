import pandas as pd
import numpy as np
import random
import math
from datetime import datetime, timedelta
from hijri_converter import convert

#############################################
# 1) دوال التحويل بين الهجري والميلادي
#############################################

def hijri_to_gregorian(h_year, h_month, h_day):
    g = convert.Hijri(h_year, h_month, h_day).to_gregorian()
    return datetime(g.year, g.month, g.day)

def gregorian_to_hijri(g_date):
    h = convert.Gregorian(g_date.year, g_date.month, g_date.day).to_hijri()
    return (h.year, h.month, h.day)

#############################################
# 2) تعريف الإجازات (بالميلادي) للطلاب والموظفين
#############################################

student_holidays = [
    (datetime(2016, 11, 10), datetime(2016, 11, 20)),
    (datetime(2017, 1, 12), datetime(2017, 1, 15)),
    (datetime(2017, 1, 15), datetime(2017, 1, 19)),
    (datetime(2017, 1, 26), datetime(2017, 1, 26)),
    (datetime(2017, 2, 4), datetime(2017, 2, 4)),
    (datetime(2017, 3, 29), datetime(2017, 4, 8)),
    (datetime(2017, 5, 11), datetime(2017, 5, 14)),
    (datetime(2017, 5, 18), datetime(2017, 5, 23)),
    (datetime(2017, 5, 25), datetime(2017, 7, 2)),
    (datetime(2017, 7, 5), datetime(2017, 8, 22)),
    (datetime(2017, 9, 10), datetime(2017, 9, 11)),
    (datetime(2017, 9, 17), datetime(2017, 9, 23)),
    (datetime(2018, 1, 11), datetime(2018, 1, 20)),
    (datetime(2018, 5, 5), datetime(2018, 5, 14)),
    (datetime(2018, 9, 2), datetime(2018, 9, 2)),
    (datetime(2018, 12, 28), datetime(2019, 1, 6)),
    (datetime(2019, 5, 5), datetime(2019, 5, 14))
]

def is_student_holiday(date_m):
    for start_h, end_h in student_holidays:
        if start_h <= date_m <= end_h:
            return True
    return False

employee_holidays = [
    (datetime(2017, 9, 23), datetime(2017, 9, 23)),
    (datetime(2018, 2, 22), datetime(2018, 2, 22)),
    (datetime(2018, 4, 1), datetime(2018, 4, 4)),
    (datetime(2019, 2, 6), datetime(2019, 2, 9)),
]

def is_employee_holiday(date_m):
    for start_h, end_h in employee_holidays:
        if start_h <= date_m <= end_h:
            return True
    return False

#############################################
# 3) وظائف الطقس
#############################################

def load_weather_data(filepath, city_name='qassim'):
    df = pd.read_csv(filepath)
    df = df[df['city'].str.lower() == city_name.lower()].copy()

    def make_datetime(row):
        return datetime(
            int(row['year']),
            int(row['month']),
            int(row['day']),
            int(row['hour']),
            int(row['minute'])
        )
    df['datetime'] = df.apply(make_datetime, axis=1)
    df['date_only'] = df['datetime'].dt.date
    return df

def get_weather_for_day(weather_df, date_obj):
    same_day = weather_df[weather_df['date_only'] == date_obj]
    if len(same_day) == 0:
        return None
    return same_day.sample(1).iloc[0].to_dict()

def weather_reduces_chances(weather_str):
    if weather_str is None:
        return 1.0
    w_lower = weather_str.lower()
    if 'sandstorm' in w_lower or 'dust' in w_lower or 'storm' in w_lower:
        return 0.3
    elif 'rain' in w_lower:
        return 0.7  # تخفيض الخروج بسبب الأمطار
    elif 'hot' in w_lower or 'cold' in w_lower:
        return 0.5  # تخفيض الخروج في الحرارة الشديدة أو البرودة الشديدة
    else:
        return 1.0

#############################################
# 4) الدالة الرئيسية لتوليد البيانات
#############################################

def main():
    people = ["abdulmalik", "aseel", "sadeem", "amal", "obaid"]
    students = ["abdulmalik", "aseel", "sadeem"]
    employee = ["amal", "obaid"]

    start_date = datetime(2017, 1, 1)
    days_num = 836
    date_list = [start_date + timedelta(days=i) for i in range(days_num)]

    weather_file_path = "/Users/a1443/PSCS/SCS/EcooVision/cleaned_data.csv"
    weather_df = load_weather_data(weather_file_path, city_name="Qassim")
    print(f"Loaded weather records: {len(weather_df)}")

    all_records = []

    for current_date in date_list:
        day_of_week = current_date.weekday()
        date_only = current_date.date()

        chosen_weather = get_weather_for_day(weather_df, date_only)
        weather_str = chosen_weather['weather'] if chosen_weather else None
        weather_factor = weather_reduces_chances(weather_str)

        is_weekend = (day_of_week == 4 or day_of_week == 5)

        go_out_all_probability = 0.3 * weather_factor
        go_out_all_together = False
        if is_weekend and random.random() < go_out_all_probability:
            go_out_all_together = True

        if is_student_holiday(current_date) or is_employee_holiday(current_date):
            if random.random() < (0.5 * weather_factor):
                go_out_all_together = True

        for person in people:
            if person in students:
                has_school = (day_of_week < 5) and (not is_student_holiday(current_date))
            else:
                has_school = (day_of_week < 5) and (not is_employee_holiday(current_date))

            if has_school:
                exit_hour = random.gauss(7.5, 0.5)  # وقت الخروج المتوقع للمدرسة أو العمل
                return_hour = exit_hour + random.gauss(5.0, 1.0)  # وقت العودة المتوقع
                return_hour = min(return_hour, 23.5)

                exit_time = datetime(current_date.year, current_date.month, current_date.day) + timedelta(hours=exit_hour)
                enter_time = datetime(current_date.year, current_date.month, current_date.day) + timedelta(hours=return_hour)

                all_records.append([
                    person, "Exit", exit_time,
                    chosen_weather['weather'] if chosen_weather else None,
                    chosen_weather['temp'] if chosen_weather else None,
                    chosen_weather['wind'] if chosen_weather else None,
                    chosen_weather['humidity'] if chosen_weather else None,
                    None
                ])
                all_records.append([
                    person, "Enter", enter_time,
                    chosen_weather['weather'] if chosen_weather else None,
                    chosen_weather['temp'] if chosen_weather else None,
                    chosen_weather['wind'] if chosen_weather else None,
                    chosen_weather['humidity'] if chosen_weather else None,
                    None
                ])

            extra_exits_num = max(0, int(np.random.poisson(0.7 * weather_factor)))

            for _ in range(extra_exits_num):
                out_hour = random.gauss(16.0, 2.0)  # خروج إضافي مساءً
                in_hour = out_hour + random.gauss(2.0, 0.5)

                if in_hour - out_hour > 4:  # لا يسمح بالبقاء خارج المنزل أكثر من 4 ساعات في الخروج الإضافي
                    in_hour = out_hour + 4

                out_time = datetime(current_date.year, current_date.month, current_date.day) + timedelta(hours=out_hour)
                in_time = datetime(current_date.year, current_date.month, current_date.day) + timedelta(hours=in_hour)

                all_records.append([
                    person, "Exit", out_time,
                    chosen_weather['weather'] if chosen_weather else None,
                    chosen_weather['temp'] if chosen_weather else None,
                    chosen_weather['wind'] if chosen_weather else None,
                    chosen_weather['humidity'] if chosen_weather else None,
                    None
                ])
                all_records.append([
                    person, "Enter", in_time,
                    chosen_weather['weather'] if chosen_weather else None,
                    chosen_weather['temp'] if chosen_weather else None,
                    chosen_weather['wind'] if chosen_weather else None,
                    chosen_weather['humidity'] if chosen_weather else None,
                    None
                ])

    df = pd.DataFrame(all_records, columns=[
        "PersonID", "Event", "Timestamp",
        "Weather", "Temp", "Wind", "Humidity",
        "NumDailyExits"
    ])

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    median_wind = df[df['Wind'] >= 0]['Wind'].median()
    df.loc[df['Wind'] < 0, 'Wind'] = median_wind

    df['Date'] = df['Timestamp'].dt.date
    df['Hour'] = df['Timestamp'].dt.hour
    df['Minute'] = df['Timestamp'].dt.minute

    data_sorted = df.sort_values(by=['PersonID', 'Timestamp'])
    cleaned_data = []
    for person in df['PersonID'].unique():
        person_data = data_sorted[data_sorted['PersonID'] == person]
        last_event = None
        for _, row in person_data.iterrows():
            if last_event == 'Exit' and row['Event'] == 'Exit':
                continue
            elif last_event == 'Enter' and row['Event'] == 'Enter':
                continue
            else:
                cleaned_data.append(row)
                last_event = row['Event']

    df = pd.DataFrame(cleaned_data)

    exit_counts = df[df["Event"]=="Exit"].groupby(["PersonID","Date"]).size().reset_index(name="ExitCount")
    df = df.merge(exit_counts, on=["PersonID","Date"], how="left")

    df["NumDailyExits"] = df["ExitCount"]
    df.drop(columns=["ExitCount"], inplace=True)

    df.sort_values(by="Timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    print("\n---------------------------------")
    print("Data generation completed!")
    print("Total records:", len(df))
    print("Preview:\n", df.head(10))

    output_file = "/Users/a1443/PSCS/SCS/EcooVision/Newsynthetic_family_data_expanded.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}.")

#############################################
# 5) تشغيل الدالة الرئيسية إذا كنا في __main__
#############################################

if __name__ == "__main__":
    main()
