import pandas as pd
import numpy as np

def create_daily_consumption_csv(filename, days=30, total_kwh=5000, variation=0.05):
    """
    Creates a CSV file with daily consumption data.

    :param filename: Name of the CSV file to create.
    :param days: Number of days in the month.
    :param total_kwh: Total monthly consumption in kWh.
    :param variation: Variation factor (e.g., 0.05 for ±5% variation).
    """
    rng = np.random.default_rng()
    base_kwh = total_kwh / days
    # Apply variation to each day
    daily_kwh = rng.uniform(base_kwh * (1 - variation), base_kwh * (1 + variation), days)
    # Adjust to match total_kwh
    scaling_factor = total_kwh / daily_kwh.sum()
    daily_kwh *= scaling_factor
    df = pd.DataFrame({'base_kw': daily_kwh})  # 'base_kw' يمثل الاستهلاك اليومي بالكيلوواط ساعة
    df.to_csv(filename, index=False)
    print(f"Created {filename} with total consumption: {df['base_kw'].sum():.2f} kWh")

# إنشاء الملفات المطلوبة
create_daily_consumption_csv('daily_data_less_6000.csv', total_kwh=5000)
create_daily_consumption_csv('daily_data_more_6000.csv', total_kwh=7000)
