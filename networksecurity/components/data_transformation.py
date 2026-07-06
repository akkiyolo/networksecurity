import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS

from networksecurity.entity.artifact_entity import(
  DataTransformationArtifact,
  DataValidationArtifact
)

from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object,read_yaml_file,write_yaml_file

class DataTransformation:
  def __init__(self,data_validation_artifact:DataValidationArtifact,
               data_transformation_artifact:DataTransformationArtifact):
    try:
      self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
      self.data_transformation_artifact:DataTransformationArtifact=data_transformation_artifact
    except Exception as e:
      raise NetworkSecurityException(e,sys)
    

  def initiate_data_transformation(self)->DataTransformationArtifact:
    logging.info("Entered initiate_data_transformation method of DataTransformation class")
    try:
      logging.info("Starting data transformation")
      train_df=DataTransformation.read_data(self,self.data_validation_artifact.valid_train_file_path)
      test_df=DataTransformation.read_data(self,self.data_validation_artifact.valid_test_file_path)

      ## training dataframe

      input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
      target_feature_train_df=train_df[TARGET_COLUMN]
    except Exception as e:
      raise NetworkSecurityException(e,sys)