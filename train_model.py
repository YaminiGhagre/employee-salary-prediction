import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. LOAD DATASET
# ============================================================

csv_path = r"C:\Users\HP\Downloads\employee_salary.csv"

df = pd.read_csv(csv_path)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", list(df.columns))


# ============================================================
# 2. REMOVE EMPLOYEE ID
# ============================================================

# employee_id is an identifier, not a salary-predicting feature
X = df.drop(columns=["salary", "employee_id"])

y = df["salary"]


# ============================================================
# 3. DEFINE FEATURES
# ============================================================

categorical_features = [
    "gender",
    "education",
    "job_title",
    "department",
    "location",
    "employment_type"
]

numeric_features = [
    "age",
    "experience_years",
    "performance_rating",
    "projects_completed",
    "overtime_hours",
    "skills_count"
]


# ============================================================
# 4. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median"))
])


categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),

    ("encoder", OneHotEncoder(
        handle_unknown="ignore"
    ))
])


preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        numeric_features
    ),

    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# ============================================================
# 5. RANDOM FOREST MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    max_depth=None
)


# ============================================================
# 6. COMPLETE ML PIPELINE
# ============================================================

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])


# ============================================================
# 7. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\nTraining model...")


# ============================================================
# 8. TRAIN
# ============================================================

pipeline.fit(
    X_train,
    y_train
)


print("Training completed!")


# ============================================================
# 9. PREDICTION
# ============================================================

y_pred = pipeline.predict(X_test)


# ============================================================
# 10. MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

mse = mean_squared_error(
    y_test,
    y_pred
)

rmse = mse ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)


print("\n====================================")
print("       MODEL PERFORMANCE")
print("====================================")

print(f"MAE  : ₹{mae:,.2f}")

print(f"MSE  : {mse:,.2f}")

print(f"RMSE : ₹{rmse:,.2f}")

print(f"R²   : {r2:.4f}")

print(f"R² % : {r2 * 100:.2f}%")

print("====================================")


# ============================================================
# 11. CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    "model",
    exist_ok=True
)


# ============================================================
# 12. SAVE MODEL
# ============================================================

model_path = "model/salary_model.pkl"

joblib.dump(
    pipeline,
    model_path
)


print("\nModel saved successfully!")

print(
    "Location:",
    os.path.abspath(model_path)
)

print("\nDone!")