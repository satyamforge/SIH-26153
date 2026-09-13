import pandas as pd
import numpy as np
import glob
import os
import joblib
import sys

sys.stdout.reconfigure(encoding="utf-8")

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix
)


# ============================================
# 1. FIND ALL CSV FILES
# ============================================

files = glob.glob("dataset/*.csv")

print(f"Found {len(files)} CSV files.")

if len(files) == 0:
    print("ERROR: No CSV files found inside dataset folder.")
    sys.exit()


# ============================================
# 2. LOAD ALL CSV FILES
# ============================================

dataframes = []

for file in files:
    print(f"\nLoading: {os.path.basename(file)}")

    try:
        df = pd.read_csv(file, low_memory=False)
        df.columns = df.columns.str.strip()

        dataframes.append(df)

        print(f"Rows loaded: {len(df):,}")

    except Exception as e:
        print(f"ERROR loading file: {e}")


# Combine everything
data = pd.concat(dataframes, ignore_index=True)

print("\n============================================")
print("DATASET LOADED")
print("============================================")
print(f"Total rows: {len(data):,}")
print(f"Total columns: {len(data.columns)}")


# ============================================
# 3. CLEAN LABELS
# ============================================

data["Label"] = data["Label"].astype(str).str.strip()

print("\nAttack categories:")
print(data["Label"].value_counts())


# ============================================
# 4. CREATE BINARY ATTACK LABEL
# ============================================

data["Attack"] = np.where(
    data["Label"].str.upper() == "BENIGN",
    0,
    1
)

print("\n============================================")
print("BINARY CLASS DISTRIBUTION")
print("============================================")

print(data["Attack"].value_counts())

print("\n0 = BENIGN")
print("1 = ATTACK")


# ============================================
# 5. SAMPLE DATA
# ============================================

# Keep a manageable number of samples
# while preserving attack/benign ratio.

MAX_SAMPLES = 500000

if len(data) > MAX_SAMPLES:

    print("\nDataset is large.")
    print(f"Creating stratified sample of {MAX_SAMPLES:,} rows...")

    data, _ = train_test_split(
        data,
        train_size=MAX_SAMPLES,
        random_state=42,
        stratify=data["Attack"]
    )

    data = data.reset_index(drop=True)

print(f"Using {len(data):,} rows for training.")


# ============================================
# 6. SEPARATE FEATURES AND LABEL
# ============================================

y = data["Attack"]

# Keep original attack category separately
attack_types = data["Label"]

X = data.drop(
    columns=["Label", "Attack"],
    errors="ignore"
)


# ============================================
# 7. CONVERT FEATURES TO NUMERIC
# ============================================

print("\nCleaning feature data...")

X = X.apply(pd.to_numeric, errors="coerce")

# Replace infinity
X.replace([np.inf, -np.inf], np.nan, inplace=True)

# Replace missing values
X = X.fillna(X.median(numeric_only=True))

X = X.fillna(0)


# ============================================
# 8. REMOVE CONSTANT FEATURES
# ============================================

constant_columns = [
    column
    for column in X.columns
    if X[column].nunique() <= 1
]

if constant_columns:

    print(
        f"Removing {len(constant_columns)} constant features."
    )

    X = X.drop(columns=constant_columns)


print(f"Final number of features: {X.shape[1]}")


# ============================================
# 9. TRAIN / TEST SPLIT
# ============================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n============================================")
print("TRAINING MODEL")
print("============================================")

print(f"Training samples: {len(X_train):,}")
print(f"Testing samples:  {len(X_test):,}")


# ============================================
# 10. RANDOM FOREST
# ============================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

print("\nTraining Random Forest...")

model.fit(X_train, y_train)


# ============================================
# 11. PREDICTIONS
# ============================================

print("\nGenerating predictions...")

predictions = model.predict(X_test)


# ============================================
# 12. EVALUATION
# ============================================

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n============================================")
print("MODEL RESULTS")
print("============================================")

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "BENIGN",
            "ATTACK"
        ]
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)


# ============================================
# 13. SAVE MODEL
# ============================================

os.makedirs("model", exist_ok=True)

model_path = "model/attack_detector.pkl"

features_path = "model/features.pkl"

joblib.dump(
    model,
    model_path
)

joblib.dump(
    X.columns.tolist(),
    features_path
)


# ============================================
# 14. SAVE DATASET INFORMATION
# ============================================

info = {
    "total_samples": len(data),
    "features": X.columns.tolist(),
    "attack_categories": attack_types.unique().tolist()
}

joblib.dump(
    info,
    "model/model_info.pkl"
)


# ============================================
# DONE
# ============================================

print("\n============================================")
print("SUCCESS! MODEL TRAINED")
print("============================================")

print(f"\nModel saved:")
print(f"  {model_path}")

print(f"\nFeatures saved:")
print(f"  {features_path}")

print("\nYour attack detection AI is ready! 🚀")