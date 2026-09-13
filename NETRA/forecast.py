
import os
import glob
import sys
import numpy as np
import pandas as pd
import joblib

sys.stdout.reconfigure(encoding="utf-8")

# ==============================
# SETTINGS
# ==============================

DATASET_FOLDER = "dataset"
MODEL_FOLDER = "model"

MAX_ROWS_PER_FILE = 30000
FORECAST_MINUTES = 5

# ==============================
# LOAD MODEL
# ==============================

print("Loading trained attack detection model...")

model = joblib.load(
    os.path.join(MODEL_FOLDER, "attack_detector.pkl")
)

features = joblib.load(
    os.path.join(MODEL_FOLDER, "features.pkl")
)

print("Model loaded.")
print(f"Expected features: {len(features)}")

# ==============================
# FIND CSV FILES
# ==============================

files = glob.glob(
    os.path.join(DATASET_FOLDER, "*.csv")
)

if not files:
    print("ERROR: No CSV files found.")
    sys.exit()

print(f"\nFound {len(files)} CSV files.")

all_data = []

# ==============================
# PROCESS EACH CSV
# ==============================

for file in files:

    print("\nLoading:", os.path.basename(file))

    df = pd.read_csv(
        file,
        low_memory=False
    )

    df.columns = df.columns.str.strip()

    print("Rows:", len(df))

    # Downsample large files
    if len(df) > MAX_ROWS_PER_FILE:

        step = max(1, len(df) // MAX_ROWS_PER_FILE)

        df = df.iloc[::step].copy()

        print(
            "Downsampled to:",
            len(df)
        )

    # ==============================
    # PREPARE MODEL FEATURES
    # ==============================

    X = pd.DataFrame(index=df.index)

    for feature in features:

        if feature in df.columns:

            X[feature] = pd.to_numeric(
                df[feature],
                errors="coerce"
            )

        else:

            X[feature] = 0

    # Clean data
    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(0)

    # ==============================
    # AI PREDICTION
    # ==============================

    print("Running AI predictions...")

    probability = model.predict_proba(X)[:, 1]

    # Actual label
    if "Label" in df.columns:

        labels = df["Label"].astype(str).values

    else:

        labels = np.array(
            ["UNKNOWN"] * len(df)
        )

    result = pd.DataFrame({

        "Attack_Probability": probability,

        "Label": labels

    })

    all_data.append(result)

# ==============================
# COMBINE
# ==============================

if not all_data:

    print("\nERROR: No usable data.")
    sys.exit()

data = pd.concat(
    all_data,
    ignore_index=True
)

print("\n================================")
print("AI PREDICTION COMPLETE")
print("================================")

print(
    "Total processed flows:",
    len(data)
)

# ==============================
# CREATE SEQUENTIAL TIME WINDOWS
# ==============================

# Each group represents one minute
# of observed network traffic.

WINDOW_SIZE = 1000

data["Window"] = (
    np.arange(len(data)) // WINDOW_SIZE
)

minute_data = (
    data
    .groupby("Window")
    .agg(

        Attack_Probability=(
            "Attack_Probability",
            "mean"
        ),

        Max_Attack_Probability=(
            "Attack_Probability",
            "max"
        ),

        Traffic_Count=(
            "Attack_Probability",
            "count"
        )

    )
    .reset_index()
)

# Create display time
start_time = pd.Timestamp(
    "2026-01-01 09:00:00"
)

minute_data["Minute"] = [
    start_time + pd.Timedelta(minutes=int(i))
    for i in minute_data["Window"]
]

# ==============================
# FORECAST
# ==============================

recent = minute_data.tail(15)

x = np.arange(len(recent))

y = recent[
    "Attack_Probability"
].values

if len(recent) >= 3:

    slope, intercept = np.polyfit(
        x,
        y,
        1
    )

else:

    slope = 0

    intercept = float(
        y.mean()
    )

future_x = np.arange(
    len(recent),
    len(recent) + FORECAST_MINUTES
)

future_probability = (
    intercept +
    slope * future_x
)

future_probability = np.clip(
    future_probability,
    0,
    1
)

last_window = int(
    minute_data["Window"].iloc[-1]
)

future = pd.DataFrame({

    "Window": range(
        last_window + 1,
        last_window +
        FORECAST_MINUTES + 1
    ),

    "Minute": [
        start_time +
        pd.Timedelta(
            minutes=last_window + i
        )
        for i in range(
            1,
            FORECAST_MINUTES + 1
        )
    ],

    "Forecast_Attack_Probability":
        future_probability

})

# ==============================
# RISK
# ==============================

current_risk = float(
    minute_data[
        "Attack_Probability"
    ].iloc[-1]
)

forecast_risk = float(
    future[
        "Forecast_Attack_Probability"
    ].max()
)

if forecast_risk >= 0.80:

    risk_level = "CRITICAL"

elif forecast_risk >= 0.60:

    risk_level = "HIGH"

elif forecast_risk >= 0.30:

    risk_level = "MEDIUM"

else:

    risk_level = "LOW"

# ==============================
# TREND
# ==============================

if slope > 0.01:

    trend = "INCREASING"

elif slope < -0.01:

    trend = "DECREASING"

else:

    trend = "STABLE"

# ==============================
# SAVE DATA
# ==============================

minute_data.to_csv(
    "forecast_history.csv",
    index=False
)

future.to_csv(
    "forecast_future.csv",
    index=False
)

# ==============================
# DISPLAY RESULTS
# ==============================

print("\n================================")
print("NETWORK ATTACK FORECAST")
print("================================")

print(
    f"Current attack probability: "
    f"{current_risk * 100:.2f}%"
)

print(
    f"Forecast attack probability: "
    f"{forecast_risk * 100:.2f}%"
)

print(
    f"Risk level: {risk_level}"
)

print(
    f"Trend: {trend}"
)

print("\nNext 5 minutes:")

for _, row in future.iterrows():

    print(
        f"{row['Minute']} -> "
        f"{row['Forecast_Attack_Probability'] * 100:.2f}%"
    )

print("\n================================")
print("FORECASTING COMPLETE")
print("================================")

print("\nFiles created:")

print("  forecast_history.csv")
print("  forecast_future.csv")
