"""
EduGrowth AI - Model Training & Validation Pipeline
Trains statistical ensemble models for:
1. Multi-class Academic Risk Level (HistGradientBoostingClassifier)
2. Expected End-Term GPA Forecaster (HistGradientBoostingRegressor)
Evaluates and serializes models with production metadata.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from feature_engineering import (
    EduGrowthFeatureEngineer,
    FEATURE_COLUMNS,
    CATEGORICAL_COLUMNS,
    TARGET_RISK,
    TARGET_GPA
)

def train_and_evaluate():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_path = os.path.join(base_dir, 'data', 'raw', 'student_cohort_data.csv')
    model_dir = os.path.join(base_dir, 'models')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    print("Loading raw cohort dataset...")
    df = pd.read_csv(raw_data_path)
    
    # 1. Feature Engineering Step
    engineer = EduGrowthFeatureEngineer()
    df_engineered = engineer.transform(df)
    
    # Save processed cohort
    processed_csv_path = os.path.join(processed_dir, 'processed_cohort.csv')
    df_engineered.to_csv(processed_csv_path, index=False)
    print(f"Processed dataset saved to: {processed_csv_path}")
    
    # Train / Test split
    X = df_engineered[FEATURE_COLUMNS + CATEGORICAL_COLUMNS]
    y_risk = df_engineered[TARGET_RISK]
    y_gpa = df_engineered[TARGET_GPA]
    
    X_train, X_test, y_risk_train, y_risk_test, y_gpa_train, y_gpa_test = train_test_split(
        X, y_risk, y_gpa, test_size=0.20, random_state=42, stratify=y_risk
    )
    
    # Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), FEATURE_COLUMNS),
            ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_COLUMNS)
        ]
    )
    
    # ---------------------------------------------------------
    # 2. Risk Classification Model (Multi-Class)
    # ---------------------------------------------------------
    print("\n--- Training Risk Classification Model ---")
    risk_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', HistGradientBoostingClassifier(
            class_weight='balanced',
            max_iter=150,
            learning_rate=0.08,
            max_depth=6,
            random_state=42
        ))
    ])
    
    risk_pipeline.fit(X_train, y_risk_train)
    y_risk_pred = risk_pipeline.predict(X_test)
    
    acc = accuracy_score(y_risk_test, y_risk_pred)
    macro_f1 = f1_score(y_risk_test, y_risk_pred, average='macro')
    weighted_f1 = f1_score(y_risk_test, y_risk_pred, average='weighted')
    cm = confusion_matrix(y_risk_test, y_risk_pred).tolist()
    
    print(f"Risk Classifier Accuracy: {acc:.4f}")
    print(f"Risk Classifier Macro F1: {macro_f1:.4f}")
    print(f"Risk Classifier Weighted F1: {weighted_f1:.4f}")
    print("Classification Report:")
    print(classification_report(y_risk_test, y_risk_pred, target_names=['Low Risk', 'Moderate Risk', 'High Risk']))
    
    # ---------------------------------------------------------
    # 3. GPA Regression Model
    # ---------------------------------------------------------
    print("\n--- Training End-Term GPA Forecaster ---")
    gpa_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.08,
            max_depth=5,
            random_state=42
        ))
    ])
    
    gpa_pipeline.fit(X_train, y_gpa_train)
    y_gpa_pred = gpa_pipeline.predict(X_test)
    
    mae = mean_absolute_error(y_gpa_test, y_gpa_pred)
    rmse = np.sqrt(mean_squared_error(y_gpa_test, y_gpa_pred))
    r2 = r2_score(y_gpa_test, y_gpa_pred)
    
    print(f"GPA Regressor MAE: {mae:.4f}")
    print(f"GPA Regressor RMSE: {rmse:.4f}")
    print(f"GPA Regressor R2 Score: {r2:.4f}")
    
    # ---------------------------------------------------------
    # 4. Feature Importance Estimation (Permutation)
    # ---------------------------------------------------------
    print("\nCalculating Feature Importance...")
    perm_importance = permutation_importance(
        risk_pipeline, X_test, y_risk_test, n_repeats=5, random_state=42, n_jobs=1
    )
    
    feature_names = FEATURE_COLUMNS + [f"dept_{cat}" for cat in risk_pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(CATEGORICAL_COLUMNS)]
    # Map back to original input column names
    raw_col_importances = {}
    for col_idx, col_name in enumerate(X.columns):
        raw_col_importances[col_name] = float(perm_importance.importances_mean[col_idx])
        
    sorted_importances = dict(sorted(raw_col_importances.items(), key=lambda item: item[1], reverse=True))
    
    # ---------------------------------------------------------
    # 5. Serialize Models and Metadata
    # ---------------------------------------------------------
    risk_model_file = os.path.join(model_dir, 'risk_classifier.joblib')
    gpa_model_file = os.path.join(model_dir, 'gpa_regressor.joblib')
    metadata_file = os.path.join(model_dir, 'model_metadata.json')
    
    joblib.dump(risk_pipeline, risk_model_file)
    joblib.dump(gpa_pipeline, gpa_model_file)
    
    metadata = {
        'model_version': '1.0.0-institutional',
        'metrics': {
            'risk_classifier': {
                'accuracy': float(acc),
                'macro_f1': float(macro_f1),
                'weighted_f1': float(weighted_f1),
                'confusion_matrix': cm
            },
            'gpa_regressor': {
                'mae': float(mae),
                'rmse': float(rmse),
                'r2_score': float(r2)
            }
        },
        'feature_columns': FEATURE_COLUMNS,
        'categorical_columns': CATEGORICAL_COLUMNS,
        'top_feature_importances': sorted_importances
    }
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print(f"\nModels and metadata successfully saved to: {model_dir}")

if __name__ == '__main__':
    train_and_evaluate()
