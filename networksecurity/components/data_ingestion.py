from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## configuration of the data ingestion config

from networksecurity.entity.config_entity import DataIngestionConfig

import os
import sys
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")

class DataIngestion:
  def __init__(self,data_ingestion_config:DataIngestionConfig):
    try:
      self.data_ingestion_config=data_ingestion_config
    except Exception as e:
      raise NetworkSecurityException(e,sys)
    

  def export_collection_as_dataframe(self):
    try:
      database_name=self.data_ingestion_config.database_name
      collection_name=self.data_ingestion_config.collection_name
      self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
      collection=self.mongo_client[database_name][collection_name]

      df=pd.DataFrame(list(collection.find()))
      if "_id" in df.columns.to_list():
        df=df.drop
    except Exception as e:
      raise NetworkSecurityException
    
  def initiate_data_ingestion(self):
    try:
      dataframe=
    except Exception as e:
      raise NetworkSecurityException
    