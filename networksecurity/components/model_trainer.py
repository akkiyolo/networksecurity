import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
  AdaBoostClassifier,
  RandomForestClassifier,
  GradientBoostingClassifier
)

class ModelTrainer:
  def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
    try:
      self.model_trainer_config=model_trainer_config
      self.data_transformation_arttifact=data_transformation_artifact
    except Exception as e:
      raise NetworkSecurityException(e,sys) 
    
  def train_model(self,X_train,y_train,X_test,y_test):
    models={
      "Random Forest": RandomForestClassifier(verbose=1),
      "Decision Tree": DecisionTreeClassifier(),
      "Gradient Boosting": GradientBoostingClassifier(verbose=1),
      "Logistic Regression": LogisticRegression(verbose=1),
      "AdaBoost":AdaBoostClassifier(),

    }
    
    
  def initiate_model_trainer(self)->ModelTrainerArtifact:
    try:
      train_file_path=self.data_transformation_arttifact.transformed_train_file_path
      test_file_path=self.data_transformation_arttifact.transformed_test_file_path

      #loading training array and testing array

      train_arr=load_numpy_array_data(train_file_path)
      test_arr=load_numpy_array_data(test_file_path)

      x_train, y_train, x_test, y_test = (
        train_arr[:, :-1], 
        train_arr[:, -1],   
        test_arr[:, :-1],   
        test_arr[:, -1],    
      )

      model=self.train_model(x_train,y_train)

    except Exception as e:
      raise NetworkSecurityException(e,sys)
