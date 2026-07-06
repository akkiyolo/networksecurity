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
    
  @staticmethod
  def read_data(file_path)->pd.DataFrame:
    try:
      return pd.read_csv(file_path)
    except Exception as e:
      raise NetworkSecurityException(e,sys)
    
  def get_data_transformer_object(cls)->Pipeline:
    """"
    It initialises a KNNImputer object with the parameters specified in the training_pipeline.py file and returns a Pipeline object with the KNNImputer object as the first step

    Args:
     cls: DataTransformation

    Returns:
     A pipeline Object
    """
    logging.info("Entered get_data_trnasformer_object method of Transformation class")

    try:
      imputer:KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
      logging.info(f"Initialise KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}")

      processor:Pipeline=Pipeline([("imputer",imputer)])

      return processor
           
    except Exception as e:
      raise NetworkSecurityException(e,sys)
    

  def initiate_data_transformation(self)->DataTransformationArtifact:
    logging.info("Entered initiate_data_transformation method of DataTransformation class")
    try:
      logging.info("Starting data transformation")
      train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
      test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
      

      ## training dataframe
      input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
      target_feature_train_df=train_df[TARGET_COLUMN]
      target_feature_train_df=target_feature_train_df.replace(-1,0)

      ## test dataframe
      input_feature_test_df=test_df.drop(columns=[TARGET_COLUMN],axis=1)
      target_feature_test_df=test_df[TARGET_COLUMN]
      target_feature_test_df=target_feature_test_df.replace(-1,0)    

    except Exception as e:
      raise NetworkSecurityException(e,sys)