"""
STEP 2: MACHINE LEARNING RISK MODEL
====================================
Builds an ML model to predict risk levels and scores for welfare cases.

In production, this would be deployed using:
- Azure Machine Learning (AML) for model training and deployment
- Azure ML Pipelines for automated retraining
- Azure ML Endpoints for real-time inference
- Model Registry for versioning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
import joblib
import os

class WelfareRiskModel:
    """
    ML model for predicting welfare case risk.
    
    Uses RandomForest for both classification (risk_level) and regression (risk_score).
    """
    
    def __init__(self):
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.regressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        self.is_trained = False
    
    def prepare_features(self, df):
        """
        Prepare features for model training/prediction.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe with welfare case data
        
        Returns:
        --------
        np.ndarray
            Feature matrix
        """
        # Encode scheme_type
        df_encoded = df.copy()
        df_encoded['scheme_type_encoded'] = self.label_encoder.fit_transform(
            df_encoded['scheme_type']
        )
        
        # Select features
        features = [
            'income',
            'last_document_update_months',
            'scheme_type_encoded',
            'past_benefit_interruptions'
        ]
        
        self.feature_names = features
        return df_encoded[features].values
    
    def train(self, X_train, y_train_level, y_train_score):
        """
        Train both classifier and regressor.
        
        Parameters:
        -----------
        X_train : np.ndarray
            Training features
        y_train_level : np.ndarray
            Risk level labels (low/medium/high)
        y_train_score : np.ndarray
            Risk score values (0-100)
        """
        # Train classifier for risk level
        self.classifier.fit(X_train, y_train_level)
        
        # Train regressor for risk score
        self.regressor.fit(X_train, y_train_score)
        
        self.is_trained = True
        print("[OK] Model training complete!")
    
    def predict_risk(self, X):
        """
        Predict risk level and score for given cases.
        
        Parameters:
        -----------
        X : np.ndarray
            Feature matrix
        
        Returns:
        --------
        tuple
            (risk_levels, risk_scores, feature_importance)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction!")
        
        # Predict risk level
        risk_levels = self.classifier.predict(X)
        
        # Predict risk score
        risk_scores = self.regressor.predict(X)
        risk_scores = np.clip(risk_scores, 0, 100)  # Ensure 0-100 range
        
        # Get feature importance
        feature_importance = self.classifier.feature_importances_
        
        return risk_levels, risk_scores, feature_importance
    
    def get_model_reasons(self, X, feature_names):
        """
        Extract model reasoning based on feature importance and values.
        
        Parameters:
        -----------
        X : np.ndarray
            Single case feature vector
        feature_names : list
            Names of features
        
        Returns:
        --------
        dict
            Dictionary with reasons for the prediction
        """
        if not self.is_trained:
            return {}
        
        # Get feature importance
        importance = self.classifier.feature_importances_
        
        # Get feature values for this case
        reasons = {}
        for i, (name, value, imp) in enumerate(zip(feature_names, X[0], importance)):
            reasons[name] = {
                'value': float(value),
                'importance': float(imp)
            }
        
        return reasons
    
    def save_model(self, filepath='welfare_risk_model.pkl'):
        """
        Save trained model to disk.
        
        In Azure ML: Models are saved to Azure ML Model Registry
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving!")
        
        model_data = {
            'classifier': self.classifier,
            'regressor': self.regressor,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, filepath)
        print(f"[OK] Model saved to: {filepath}")
    
    def load_model(self, filepath='welfare_risk_model.pkl'):
        """
        Load trained model from disk.
        
        In Azure ML: Models are loaded from Azure ML Model Registry
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        self.classifier = model_data['classifier']
        self.regressor = model_data['regressor']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.is_trained = True
        print(f"[OK] Model loaded from: {filepath}")

def train_risk_model():
    """
    Main function to train the risk model.
    """
    print("=" * 60)
    print("STEP 2: TRAINING ML RISK MODEL")
    print("=" * 60)
    
    # Load dataset
    if not os.path.exists('welfare_cases_dataset.csv'):
        raise FileNotFoundError("Dataset not found! Run step1_generate_dataset.py first.")
    
    df = pd.read_csv('welfare_cases_dataset.csv')
    print(f"\n[OK] Loaded dataset: {len(df)} cases")
    
    # Initialize model
    model = WelfareRiskModel()
    
    # Prepare features
    X = model.prepare_features(df)
    
    # Prepare targets
    y_level = df['risk_level'].values
    y_score = df['risk_score'].values
    
    # Split data
    X_train, X_test, y_level_train, y_level_test, y_score_train, y_score_test = \
        train_test_split(X, y_level, y_score, test_size=0.2, random_state=42)
    
    print(f"[OK] Training set: {len(X_train)} cases")
    print(f"[OK] Test set: {len(X_test)} cases")
    
    # Train model
    print("\nTraining model...")
    model.train(X_train, y_level_train, y_score_train)
    
    # Evaluate model
    print("\n" + "=" * 60)
    print("MODEL EVALUATION:")
    print("=" * 60)
    
    # Predict on test set
    y_level_pred, y_score_pred, _ = model.predict_risk(X_test)
    
    # Classification accuracy
    accuracy = accuracy_score(y_level_test, y_level_pred)
    print(f"\n[OK] Risk Level Classification Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_level_test, y_level_pred))
    
    # Regression MSE
    mse = mean_squared_error(y_score_test, y_score_pred)
    rmse = np.sqrt(mse)
    print(f"\n[OK] Risk Score RMSE: {rmse:.2f}")
    
    # Feature importance
    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE:")
    print("=" * 60)
    feature_importance = model.classifier.feature_importances_
    for name, importance in zip(model.feature_names, feature_importance):
        print(f"  {name}: {importance:.3f}")
    
    # Save model
    model.save_model()
    
    # Example prediction
    print("\n" + "=" * 60)
    print("EXAMPLE PREDICTION:")
    print("=" * 60)
    sample_idx = 0
    sample_case = X_test[sample_idx:sample_idx+1]
    pred_level, pred_score, _ = model.predict_risk(sample_case)
    
    print(f"\nSample Case Features:")
    for name, value in zip(model.feature_names, sample_case[0]):
        print(f"  {name}: {value:.2f}")
    
    print(f"\nPredicted Risk Level: {pred_level[0]}")
    print(f"Predicted Risk Score: {pred_score[0]:.2f}")
    print(f"Actual Risk Level: {y_level_test[sample_idx]}")
    print(f"Actual Risk Score: {y_score_test[sample_idx]:.2f}")
    
    print("\n" + "=" * 60)
    print("[OK] Model training complete!")
    print("=" * 60)
    print("\nNOTE: In production, this would be deployed using:")
    print("  - Azure Machine Learning for training and deployment")
    print("  - Azure ML Pipelines for automated retraining")
    print("  - Azure ML Endpoints for real-time inference")
    print("  - Azure ML Model Registry for versioning")
    
    return model

if __name__ == "__main__":
    train_risk_model()

