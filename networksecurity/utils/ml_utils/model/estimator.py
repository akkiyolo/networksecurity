from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR, MODEL_FILE_NAME

import os 
import sys  

from networksecurity.exception.exception import NetworkSecurityException  # Custom error handler
from networksecurity.logging.logger import logging  # Custom logger

class NetworkModel:
    def __init__(self, preprocessor, model):
        try:
            self.preprocessor = preprocessor  # Store the preprocessor (KNN Imputer pipeline)
            self.model = model  # Store the trained ML model
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def predict(self, x):
        try:
            # Step 1: Preprocess the raw data (fill missing values, etc.)
            x_transform = self.preprocessor.transform(x)
            
            # Step 2: Run the ML model on the preprocessed data to get predictions
            y_hat = self.model.predict(x_transform)
            
            return y_hat  # Return predictions (array of 0s and 1s)
        except Exception as e:
            raise NetworkSecurityException(e, sys)