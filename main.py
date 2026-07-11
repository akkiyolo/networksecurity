from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation,DataValidationConfig
from networksecurity.components.data_transformation import DataTransformation,DataTransformationConfig,DataTransformationArtifact
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.components.model_trainer import ModelTrainer

import sys

if __name__=="__main__":
  try: 
    trainingpipelineconfig=TrainingPipelineConfig()
    dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
    data_ingestion=DataIngestion(dataingestionconfig)
    logging.info("Initiate the data ingestion")
    dataingestionartifact=data_ingestion.initiate_data_ingestion()
    logging.info("Data Initiation Completed")
    print(dataingestionartifact)
    data_validation_config=DataValidationConfig(trainingpipelineconfig)
    data_validation=DataValidation(dataingestionartifact,data_validation_config)
    logging.info("Initiate the data validation")
    data_validation_artifact=data_validation.initiate_data_validation()
    logging.info("data validation completed")
    print(data_validation_artifact)
    data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
    data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
    data_transformation_artifact=data_transformation.initiate_data_transformation()
    logging.info("Data Transformation completed successfully.")

    logging.info("Model tarining started")
    model_trainer_config=ModelTrainerConfig(trainingpipelineconfig)
    model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
    model_trainer_artifact=model_trainer.initiate_model_trainer()

    logging.info("Model Training artifact created")

  except Exception as e:
    raise NetworkSecurityException(e,sys)
