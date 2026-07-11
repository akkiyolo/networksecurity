import os  # For file/directory operations
import sys  # For system-level error info

from networksecurity.exception.exception import NetworkSecurityException  # Custom error handler
from networksecurity.logging.logger import logging  # Custom logger

from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact  # Input/output artifacts
from networksecurity.entity.config_entity import ModelTrainerConfig  # WHERE to save the model



from networksecurity.utils.ml_utils.model.estimator import NetworkModel  # Wraps preprocessor + model into one object
from networksecurity.utils.main_utils.utils import save_object, load_object  # Save/load pickle files
from networksecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models  # Load arrays, evaluate models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score  # Calculate F1, precision, recall

# Import all the ML models we want to try
from sklearn.linear_model import LogisticRegression  # Simple linear classifier
from sklearn.metrics import r2_score  # R-squared score for model evaluation
from sklearn.neighbors import KNeighborsClassifier  # KNN classifier (imported but not used)
from sklearn.tree import DecisionTreeClassifier  # Decision tree classifier
from sklearn.ensemble import (
    AdaBoostClassifier,  # Adaptive Boosting ensemble
    GradientBoostingClassifier,  # Gradient Boosting ensemble
    RandomForestClassifier,  # Random Forest ensemble
)

class ModelTrainer:

    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        """Store the config (where to save) and artifact (where to read transformed data from)."""
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
      
    def train_model(self, X_train, y_train, x_test, y_test):


        models = {
                "Random Forest": RandomForestClassifier(verbose=1),  # verbose=1 prints progress during training
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }

        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy', 'log_loss'],  
            },
            "Random Forest": {
                # 'criterion':['gini', 'entropy', 'log_loss'],
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8, 16, 32, 128, 256]  # Number of trees in the forest
            },
            "Gradient Boosting": {
                # 'loss':['log_loss', 'exponential'],
                'learning_rate': [.1, .01, .05, .001],  # How fast the model learns
                'subsample': [0.6, 0.7, 0.75, 0.85, 0.9],  # Fraction of data used per tree
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8, 16, 32, 64, 128, 256]  # Number of boosting stages
            },
            "Logistic Regression": {}, 
            "AdaBoost": {
                'learning_rate': [.1, .01, .001],  
                'n_estimators': [8, 16, 32, 64, 128, 256] 
            }
            
        }
        
        model_report: dict = evaluate_models(X_train=X_train, y_train=y_train, X_test=x_test, y_test=y_test,
                                          models=models, param=params)
        
        ## Find the BEST model — the one with the highest test score
        best_model_score = max(sorted(model_report.values()))

        ## Get the NAME of the best model from the report dictionary
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        
        # Get the actual model OBJECT (not just the name)
        best_model = models[best_model_name]

        y_train_pred = best_model.predict(X_train)

        # Calculate F1, precision, recall for TRAINING data
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)


        # Make predictions on the TEST data to calculate test metrics
        y_test_pred = best_model.predict(x_test)
        
        # Calculate F1, precision, recall for TEST data
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)


        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        # Create the directory for saving the trained model
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
        
        # Save the NetworkModel class reference to the artifacts directory
        save_object(self.model_trainer_config.trained_model_file_path, obj=NetworkModel)
        
        # Save JUST the best model (without preprocessor) to final_model/ for production use
        # This is what app.py loads when making predictions
        save_object("final_model/model.pkl", best_model)
        

        ## Create the Model Trainer Artifact — records what this step produced
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,  # Training performance
                             test_metric_artifact=classification_test_metric  # Testing performance
                             )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact
    
        
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            # Get the file paths for transformed data from the previous step's artifact
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            # Load the numpy arrays from .npy files
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],  # Training features
                train_arr[:, -1],   # Training target
                test_arr[:, :-1],   # Testing features
                test_arr[:, -1],    # Testing target
            )

            # Train all models and get the artifact for the best one
            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            return model_trainer_artifact

            
        except Exception as e:
            raise NetworkSecurityException(e, sys)