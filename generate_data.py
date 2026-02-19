import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
start = datetime(2023, 1, 1)
records = []

for i in range(730):
    date = start + timedelta(days=i)
    dow = date.weekday()
    month = date.month

    weekday_factor = [1.15, 1.10, 1.00, 0.98, 1.02, 0.85, 0.80][dow]
    seasonal_factor = 1.20 if month in [12, 1, 2] else 1.0
    anomaly = 1.35 if (date.year == 2023 and date.isocalendar()[1] == 10) else 1.0

    base_arrivals = 120
    arrivals = int(base_arrivals * weekday_factor * seasonal_factor * anomaly * np.random.uniform(0.9, 1.1))

    staff_on_duty = max(8, int(np.random.normal(18, 2)))
    crowding_ratio = arrivals / (staff_on_duty * 6.5)

    avg_wait = round(np.clip(25 + crowding_ratio * 40 + np.random.normal(0, 5), 10, 180), 1)
    avg_los = round(avg_wait * 1.8 + np.random.normal(0, 15), 1)

    admitted = int(arrivals * np.random.uniform(0.18, 0.28))
    discharged = int(arrivals * np.random.uniform(0.55, 0.70))
    left_without_seen = int(arrivals * np.clip(crowding_ratio * 0.05, 0.01, 0.12))
    transferred = max(0, arrivals - admitted - discharged - left_without_seen)

    satisfaction = round(np.clip(9 - (avg_wait / 30) + np.random.normal(0, 0.4), 1, 10), 1)

    records.append({
        "date": date.strftime("%Y-%m-%d"),
        "day_of_week": date.strftime("%A"),
        "month": date.strftime("%B"),
        "year": date.year,
        "shift": np.random.choice(["Day", "Evening", "Night"], p=[0.40, 0.35, 0.25]),
        "total_arrivals": arrivals,
        "staff_on_duty": staff_on_duty,
        "crowding_ratio": round(crowding_ratio, 2),
        "avg_wait_min": avg_wait,
        "avg_los_min": round(avg_los, 1),
        "admitted": admitted,
        "discharged": discharged,
        "left_without_seen": left_without_seen,
        "transferred": transferred,
        "triage_critical": int(arrivals * 0.03),
        "triage_urgent": int(arrivals * 0.18),
        "triage_semi_urgent": int(arrivals * 0.45),
        "triage_non_urgent": int(arrivals * 0.34),
        "patient_satisfaction": satisfaction,
    })

pd.DataFrame(records).to_csv("hospital_ed_data.csv", index=False)
print("Done.")
