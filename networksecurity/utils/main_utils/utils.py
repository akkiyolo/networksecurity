import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os,sys
import numpy as np
import dill
import pickle

def read_yaml_file(file_path:str) -> dict:
  try:
    with open(file_path,"rb") as yaml_file:
      return yaml.safe_load(yaml_file)
    
  except Exception as e:
    raise NetworkSecurityException(e,sys) from e
  
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            yaml.dump(content, file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def save_numpy_array_data(file_path: str, array: np.ndarray):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
   
def save_object(file_path: str, obj: object) -> None:
    try:
        logging.info("Entered the save_object method of MainUtils class")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Open the file in binary write mode and dump the object
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)  # Serialize the object to the file
        logging.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e