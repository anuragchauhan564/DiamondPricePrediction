from sklearn.impute import SimpleImputer  ## Handling Missing Values
from sklearn.preprocessing import StandardScaler ## Handling Feature Selection 
from sklearn.preprocessing import OrdinalEncoder ## Ordinal Encodering
from sklearn.pipeline import Pipeline ##Pipeline
from sklearn.compose import ColumnTransformer

import os, sys
import numpy as np
import pandas as pd 
from dataclasses import dataclass 

from src.logger import logging
from src.exception import CustomException
from src.utils import save_object

## Data Transformation config
@dataclass
class DataTransformationconfig:
    prepocessor_obj_file_path = os.path.join('artifacts','preprocessor.pkl')


## Data Ingestion Config Class 

class DataTranformation:
    def __init__(self):
        self.data_transformation_config =DataTransformationconfig()

    def  get_data_transformation_object(self):

        try:
            logging.info("Data Transformation intiated")
            ## Define which columns should be ordinal-encoded ans which should be scaled
            categorical_cols = ['cut','color','clarity']
            numerical_cols = ['carat','depth','table','x','y','z']

            ## Define the custom ranking for each ordinal variable
            cut_categories = ['Fair','Good','Very Good','Premium','Ideal']
            color_categories = ['D','E','F','G','H','I','J']
            clarity_categories = ['I1','SI1','SI2','VS2','VS1','VVS2','VVS1','IF']

            logging.info("Pileline Initiated")
             
            ## Numerical Pipline
            num_pipline = Pipeline(
               steps=[
               ('imputer',SimpleImputer(strategy='median')),
               ('scaler',StandardScaler())
               ]

            )

            ## Categorical pipline
            cut_pipline = Pipeline(
                steps=[
                ('impoter',SimpleImputer(strategy='most_frequent')),
                ('ordinalencoder',OrdinalEncoder(categories=[cut_categories,color_categories,clarity_categories])),
                ('scaler', StandardScaler())
                ]
            
            )

            preprocessor = ColumnTransformer([
            ('num_pipline',num_pipline,numerical_cols),
            ('cat_pipline',cut_pipline,categorical_cols)
            ])

            return preprocessor
        
            logging.info("Pipeline Completed")

        except Exception as e:
            logging.info('Error in Data Transformation')
            raise CustomException(e,sys)

    def initiate_data_transformation(self,train_path,test_path):

        try:
            #Reading train and test data
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info('Read train and test data Completed')
            logging.info(f'Train Dataframe Head : \n{train_df.head().to_string()}')
            logging.info(f'Test Dataframe Head : \n {test_df.head().to_string()}')

            logging.info("Obtaining preprocessing object")

            preprocessing_obj = self.get_data_transformation_object()

            target_column_name = 'price'
            drop_columns = [target_column_name,'id']


            ## features into independent and dependent features

            input_feature_train_df = train_df.drop(columns=drop_columns,axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=drop_columns,axis=1)
            tatget_feature_test_df = test_df[target_column_name]


            ## Apply the transformation 
            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            logging.info('Applying preprocessing on trsining and testing dataset.')
            train_arr = np.c_[input_feature_train_arr,np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr,np.array(tatget_feature_test_df)]


            save_object(
                file_path=self.data_transformation_config.prepocessor_obj_file_path,
                obj=preprocessing_obj
            )

            logging.info("Processor pickle in created and save")

            return(
                train_arr,
                test_arr,
                self.data_transformation_config.prepocessor_obj_file_path
            )
        except Exception as e:
            logging.info("Exception occured in the initiate_datatrandormation")

            raise CustomException(e,sys)




