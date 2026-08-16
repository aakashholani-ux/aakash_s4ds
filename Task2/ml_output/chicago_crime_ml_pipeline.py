import pandas as pd
import numpy as np
import os
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve
)

# Configuration
DATASET_PATH = r"C:\Users\Aakash Holani\OneDrive\Desktop\Tasks\Task1\eda_output\chicago_crime_dataset.csv"
OUTPUT_DIR = "ml_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
RANDOM_STATE = 42

def save_fig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{name}.png"), dpi=150)
    plt.close()

def parse_mixed_dates(series):
    parsed = pd.to_datetime(series, format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    mask = parsed.isna()
    parsed[mask] = pd.to_datetime(series[mask], format="%m-%d-%Y %H:%M", errors="coerce")
    return parsed

print("Loading data...")
df = pd.read_csv(DATASET_PATH)

print("Feature Engineering...")
df["Date_parsed"] = parse_mixed_dates(df["Date"])
df = df.dropna(subset=["Date_parsed"])

df["hour"] = df["Date_parsed"].dt.hour
df["day_of_week"] = df["Date_parsed"].dt.dayofweek
df["month"] = df["Date_parsed"].dt.month
df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
df["is_night"] = ((df["hour"] >= 21) | (df["hour"] <= 5)).astype(int)

df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)
df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)

leaky_irrelevant = [
    "ID", "Case Number", "Date", "Date_parsed", "Updated On",
    "Block", "Description", "IUCR", "FBI Code", 
    "X Coordinate", "Y Coordinate", "Latitude", "Longitude", "Location", "_year",
    "hour", "day_of_week", "month"
]
df = df.drop(columns=leaky_irrelevant, errors="ignore")

df["Location Description"] = df["Location Description"].fillna("OTHER")
df["Community Area"] = df["Community Area"].fillna(-1).astype(int).astype(str)
df["District"] = df["District"].astype(str)
df["Ward"] = df["Ward"].astype(str)
df["Beat"] = df["Beat"].astype(str)
df["Arrest"] = df["Arrest"].astype(int)

categorical_features = ["Primary Type", "Location Description", "District", "Beat", "Ward", "Community Area"]
for col in categorical_features:
    df[col] = df[col].astype("category")

numerical_features = [
    "hour_sin", "hour_cos", "month_sin", "month_cos", "dow_sin", "dow_cos", 
    "is_weekend", "is_night", "Domestic"
]
df["Domestic"] = df["Domestic"].astype(int)

print("Preparing modeling arrays...")
X = df[numerical_features + categorical_features]
y = df["Arrest"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

print("Defining preprocessor...")
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ], remainder="drop"
)

models = {
    "Logistic Regression": LogisticRegression(class_weight="balanced", max_iter=1000, random_state=RANDOM_STATE),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=15, class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE)
}

results = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

for name, model in models.items():
    print(f"\n--- Training {name} ---")
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])
    
    cv_scores = {"accuracy": [], "precision": [], "recall": [], "f1": [], "roc_auc": []}
    
    print("Running 5-fold CV...")
    fold = 1
    for train_idx, val_idx in cv.split(X_train, y_train):
        X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
        X_va, y_va = X_train.iloc[val_idx], y_train.iloc[val_idx]
        
        pipeline.fit(X_tr, y_tr)
        y_va_pred = pipeline.predict(X_va)
        y_va_prob = pipeline.predict_proba(X_va)[:, 1]
        
        cv_scores["accuracy"].append(accuracy_score(y_va, y_va_pred))
        cv_scores["precision"].append(precision_score(y_va, y_va_pred))
        cv_scores["recall"].append(recall_score(y_va, y_va_pred))
        cv_scores["f1"].append(f1_score(y_va, y_va_pred))
        cv_scores["roc_auc"].append(roc_auc_score(y_va, y_va_prob))
        print(f"  Fold {fold} done.")
        fold += 1
        
    print("Fitting on full training set...")
    pipeline.fit(X_train, y_train)
    
    print("Evaluating on test set...")
    y_test_pred = pipeline.predict(X_test)
    y_test_prob = pipeline.predict_proba(X_test)[:, 1]
    
    test_metrics = {
        "accuracy": accuracy_score(y_test, y_test_pred),
        "precision": precision_score(y_test, y_test_pred),
        "recall": recall_score(y_test, y_test_pred),
        "f1": f1_score(y_test, y_test_pred),
        "roc_auc": roc_auc_score(y_test, y_test_prob),
        "pr_auc": average_precision_score(y_test, y_test_prob)
    }
    
    results[name] = {
        "cv_mean": {k: np.mean(v) for k, v in cv_scores.items()},
        "cv_std": {k: np.std(v) for k, v in cv_scores.items()},
        "test": test_metrics,
        "pipeline": pipeline
    }
    
    cm = confusion_matrix(y_test, y_test_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title(f"Confusion Matrix: {name}")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    save_fig(f"cm_{name.replace(' ', '_').lower()}")
    
    fpr, tpr, _ = roc_curve(y_test, y_test_prob)
    results[name]["roc"] = (fpr.tolist(), tpr.tolist())
    
    p, r, _ = precision_recall_curve(y_test, y_test_prob)
    results[name]["pr"] = (p.tolist(), r.tolist())

plt.figure(figsize=(8, 6))
for name in models.keys():
    fpr, tpr = results[name]["roc"]
    plt.plot(fpr, tpr, label=f"{name} (AUC={results[name]['test']['roc_auc']:.3f})")
plt.plot([0, 1], [0, 1], "k--")
plt.title("ROC Curves")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend()
save_fig("roc_curves")

plt.figure(figsize=(8, 6))
for name in models.keys():
    p, r = results[name]["pr"]
    plt.plot(r, p, label=f"{name} (AUC={results[name]['test']['pr_auc']:.3f})")
plt.title("Precision-Recall Curves")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.legend()
save_fig("pr_curves")

print("Saving models and metrics...")
for name in models.keys():
    pipeline = results[name].pop("pipeline")
    joblib.dump(pipeline, os.path.join(OUTPUT_DIR, f"{name.replace(' ', '_').lower()}.joblib"))

with open(os.path.join(OUTPUT_DIR, "metrics.json"), "w") as f:
    json.dump(results, f, indent=4)

print("Extracting feature importances for Random Forest...")
rf_pipeline = joblib.load(os.path.join(OUTPUT_DIR, "random_forest.joblib"))
rf_model = rf_pipeline.named_steps["classifier"]
preprocessor = rf_pipeline.named_steps["preprocessor"]

cat_encoder = preprocessor.named_transformers_["cat"]
cat_feature_names = cat_encoder.get_feature_names_out(categorical_features)
all_feature_names = numerical_features + list(cat_feature_names)

importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1][:20]

plt.figure(figsize=(10, 8))
plt.barh(range(len(indices)), importances[indices][::-1], align="center")
plt.yticks(range(len(indices)), [all_feature_names[i] for i in indices][::-1])
plt.title("Top 20 Feature Importances (Random Forest)")
plt.xlabel("Importance")
save_fig("rf_feature_importances")

print("Pipeline completed successfully!")
