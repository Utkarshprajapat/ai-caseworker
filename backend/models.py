"""
ML Risk Model Wrapper - Production Ready
Handles welfare case risk prediction using pre-trained RandomForest models.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class WelfareRiskModel:
    """
    ML model for predicting welfare case risk.
    
    Uses RandomForest for both classification (risk_level) and regression (risk_score).
    """
    
    def __init__(self):
        self.classifier = None
        self.regressor = None
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
    
    def load_model(self, filepath='welfare_risk_model.pkl'):
        """
        Load trained model from disk.
        
        Parameters:
        -----------
        filepath : str
            Path to the model file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        try:
            model_data = joblib.load(filepath)
            self.classifier = model_data['classifier']
            self.regressor = model_data['regressor']
            self.label_encoder = model_data['label_encoder']
            self.feature_names = model_data['feature_names']
            self.is_trained = True
            logger.info(f"✅ Model loaded successfully from: {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to load model from {filepath}: {e}")
            raise


