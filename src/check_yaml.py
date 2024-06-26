import yaml
import validators
import pandas as pd
import numpy as np
from datetime import datetime
from constants import LOCAL_DIRECTORY

STUDY_yaml = LOCAL_DIRECTORY + 'STUDY.yaml'
EXPERMENT_yaml = LOCAL_DIRECTORY + 'EXPERIMENTS.yaml' 
COMPARTMENT_yaml = LOCAL_DIRECTORY + 'COMPARTMENTS.yaml'
COMMUNITY_MEM_yaml = LOCAL_DIRECTORY + 'COMMUNITY_MEMBERS.yaml'
COMMUNITIES_yaml = LOCAL_DIRECTORY + 'COMMUNITIES.yaml'
PERTURBATION_yaml = LOCAL_DIRECTORY + 'PERTURBATIONS.yaml'


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
    

def test_study_yaml(data):
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Study_UniqueID':
            if not (pd.api.types.is_float_dtype(df[column]) or pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Column '{column}' must be of type string or blank.")
        else:
            if not (pd.api.types.is_string_dtype(df[column])):
                 errors.append(f"Column '{column}' must be of type a string. No blank celds allowed.")
    return errors

def test_experiments_yaml(data):
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Biological_Replicates_Number':
            if not (pd.api.types.is_numeric_dtype(df[column])):
                errors.append(f"Column '{column}' must be of  must a numeric value. No blank celds allowed.")
        elif column == 'Control_Description':
            if not (pd.api.types.is_float_dtype(df[column]) or pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Column '{column}' must be of type string or blank.")
        else:
            if not (pd.api.types.is_string_dtype(df[column])):
                 errors.append(f"Column '{column}' must be of type a string. No blank celds allowed.")
    return errors

def test_compartments_yaml(data):
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Compartment_ID' or column == 'Medium_Name':
            if not (pd.api.types.is_string_dtype(df[column])):
                 errors.append(f"Column '{column}' must be of type a string. No blank celds allowed.")
        elif column == 'Compartment_StirringMode' or column == 'Medium_Link':
            if not (pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                 errors.append(f"Column '{column}' must be of type string or blank.")
        elif column == 'Compartment_Volume' or column == 'O2%' or column == 'Inoculum_Concentration' or column == 'Inoculum_Volume':
            if not (pd.api.types.is_numeric_dtype(df[column])):
                errors.append(f"Column '{column}' must be of  must a numeric value. No blank celds allowed.")
        elif column == 'Carbon_Source':
            if not (df[column].isin([0, 1]).all() or pd.api.types.is_float_dtype(df[column])):
                errors.append(f"Values in column '{column}' must be 0, 1, or blank.")
        else:
            if not (pd.api.types.is_numeric_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                errors.append(f"Column '{column}' must be of  must a numeric or blank value.")
    return errors


def test_comu_members_yaml(data):
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Defined':
            if not df[column].isin([0, 1]).all():
                errors.append(f"Column '{column}' must be of  must 0 or 1. No blank celds allowed.")
        elif column == 'NCBI_ID':
            if not (pd.api.types.is_numeric_dtype(df[column])):
                errors.append(f"Column '{column}' must be of  must a numeric value. No blank celds allowed.")
        elif column == 'Description':
            if not (pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                errors.append(f"Column '{column}' must be of type string or blank.")
        else:
            if not (pd.api.types.is_string_dtype(df[column])):
                 errors.append(f"Column '{column}' must be of type a string. No blank celds allowed.")
    return errors

def test_communities_yaml(data):
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if not pd.api.types.is_string_dtype(df[column]):
                 errors.append(f"Column '{column}' must be of type a string. No blank celds allowed.")
    
    return errors

def test_perturbation_yaml(data):
    df = pd.DataFrame(data)
    errors = []
    if pd.api.types.is_string_dtype(df['Perturbation_ID']):
        for column in df.columns:
            if column == 'Experiment_ID' or column == 'Perturbation_Description' or column == 'Perturbation_EndTime' or column == 'Perturbation_StartTime':
                if not (pd.api.types.is_string_dtype(df[column])):
                 errors.append(f"Column '{column}' must be of type a string. No blank celds allowed.")
            elif column == 'Perturbation_MaximumValue' or column == 'Perturbation_MinimumValue':
                if not (pd.api.types.is_numeric_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                    errors.append(f"Column '{column}' must be of  must a numeric or blank value.")
            else:
                if not (pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                    errors.append(f"Column '{column}' must be of type string or blank.")
    if pd.api.types.is_string_dtype(df['OLD_Community_ID']):
        if not (pd.api.types.is_string_dtype(df['NEW_Community_ID'])):
                 errors.append("Column 'NEW_Community_ID' must be of type a string. No blank celds allowed.")
    if pd.api.types.is_string_dtype(df['OLD_Compartment_ID']):
        if not (pd.api.types.is_string_dtype(df['NEW_Compartment_ID'])):
                 errors.append("Column 'NEW_Compartment_ID' must be of type a string. No blank celds allowed.")
    if (pd.api.types.is_numeric_dtype(df['Perturbation_MaximumValue']) and pd.api.types.is_numeric_dtype(df['Perturbation_MinimumValue'])):
        logic_check = df['Perturbation_MaximumValue'] > df['Perturbation_MinimumValue']
        if not logic_check.all():
            errors.append("Column 'Perturbation_MaximumValue' must be bigger than 'Perturbation_MinimumValue'.")
    if (pd.api.types.is_string_dtype(df['Perturbation_EndTime']) and pd.api.types.is_string_dtype(df['Perturbation_StartTime'])):
        df['Perturbation_EndTime'] = pd.to_datetime(df['Perturbation_EndTime']).dt.time
        df['Perturbation_StartTime'] = pd.to_datetime(df['Perturbation_StartTime']).dt.time
        logic_check = df['Perturbation_EndTime'] > df['Perturbation_StartTime']
        if not logic_check.all():
            errors.append("'Perturbation_EndTime' must be bigger than 'Perturbation_StartTime'.")


    return errors
        



    
data_study_yaml = load_yaml(STUDY_yaml)
errors = test_study_yaml(data_study_yaml)

data_experiment_yaml = load_yaml(EXPERMENT_yaml)
errors2 = test_experiments_yaml(data_experiment_yaml)
data_compartment_yaml = load_yaml(COMPARTMENT_yaml)
errors3 = test_compartments_yaml(data_compartment_yaml)

data_comu_members_yaml = load_yaml(COMMUNITY_MEM_yaml)
errors4 = test_comu_members_yaml(data_comu_members_yaml)

data_comu = load_yaml(COMMUNITIES_yaml)
errors5 = test_communities_yaml(data_comu)

data_pertu = load_yaml(PERTURBATION_yaml)
errors6 = test_perturbation_yaml(data_pertu)
print(errors, errors2, errors3,errors4,errors6)
print(type(data_pertu['NEW_Community_ID'][0]))