# loads the initial pokemon csv file to a Google BigQuery table for us to later pull from, perform data transformations on, carry out our pokebattler functions and send the new data returned back up to the BigQuery table.

from google.cloud import bigquery
import logging
from logging import INFO
import pandas as pd
import pandas_gbq
import sys

def df_import(csv_file):
    poke_df = pd.read_csv(csv_file)
    return poke_df

def df_drop_add(dataframe):
    """
    ## df_drop_add(dataframe)
    removes a specific list of columns & adds a 'wins' and 'losses' column
    *dataframe:
    - takes a pandas dataframe
    """
    #rename name column
    dataframe.rename(columns={"english_name": "name"}, inplace=True)
    # Columns to drop from dataframe
    dataframe.drop(columns=[
        'japanese_name',
        'percent_male',
        'percent_female',
        'capture_rate',
        'base_egg_steps',
        'evochain_0',
        'evochain_1',
        'evochain_2',
        'evochain_3',
        'evochain_4',
        'evochain_5',
        'evochain_6',
        'gigantamax',
        'mega_evolution',
        'mega_evolution_alt',
    ],   
        axis=1,
        inplace=True,
    )
    # Columns to add to dataframe
    col_list=['wins','losses','times_chosen']
    for col in col_list:
        if col not in dataframe.columns:
            dataframe['wins']=0
            dataframe['losses']=0
            dataframe['times_chosen']=0
        else:
            pass
    return dataframe


logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=INFO,
                    stream=sys.stderr)
logger: logging.Logger = logging

def load_to_gbq() -> None:
    """
    creates a Google BigQuery dataset and table, and loads a pandas dataframe to it
    """
    # Instantiate bigquery client api which will create a dataset
    client = bigquery.Client()
    # Tell the client to use "poke_battler_table" as the dataset name to create in the project
    dataset_id = f"{client.project}.poke_battler_data"
    # Pass dataset_id to bigquery's Dataset class to build a reference
    dataset = bigquery.Dataset(dataset_id)
    # Assign the dataset's server location to US
    dataset.location = "US"
    # Tell the client to create the dataset on google bigquery with the completed information
    dataset = client.create_dataset(dataset, exists_ok=False, timeout=30)
    # If successful, log the creation of the dataset
    logger.info(f"Created dataset: '{dataset.dataset_id}' in '{client.project}'.")


    # Project to look for when creating a table,
    project_id = "deb-01-346205"
    # dataset to insert the table into
    table_id = "poke_battler_data.pokemon"
    poke_df = df_import('pokemon.csv')
    # Loading transformed dataframe into google big query with the specified project/dataset as targets and a specified table schema.
    logger.info(f"Loading dataframe to: '{dataset.dataset_id}'...")
    poke_df = df_drop_add(poke_df) 
    pandas_gbq.to_gbq(poke_df, table_id, project_id=project_id, if_exists="fail", api_method="load_csv", table_schema=[
        {'name': 'national_number', 'type': 'INT64'}, 
        {'name': 'gen', 'type': 'STRING'}, 
        {'name': 'name', 'type': 'STRING'}, 
        {'name': 'primary_type', 'type': 'STRING'}, 
        {'name': 'secondary_type', 'type': 'STRING'}, 
        {'name': 'classification', 'type': 'STRING'}, 
        {'name': 'height_m', 'type': 'FLOAT64'}, 
        {'name': 'weight_kg', 'type': 'FLOAT64'}, 
        {'name': 'hp', 'type': 'INT64'}, 
        {'name': 'attack', 'type': 'INT64'}, 
        {'name': 'defense', 'type': 'INT64'}, 
        {'name': 'sp_attack', 'type': 'INT64'}, 
        {'name': 'sp_defense', 'type': 'INT64'}, 
        {'name': 'speed', 'type': 'INT64'}, 
        {'name': 'abilities_0', 'type': 'STRING'}, 
        {'name': 'abilities_1', 'type': 'STRING'}, 
        {'name': 'abilities_2', 'type': 'STRING'},
        {'name': 'abilities_hidden', 'type': 'STRING'},
        {'name': 'against_normal', 'type': 'FLOAT64'},
        {'name': 'against_fire', 'type': 'FLOAT64'},
        {'name': 'against_water', 'type': 'FLOAT64'},
        {'name': 'against_electric', 'type': 'FLOAT64'},
        {'name': 'against_grass', 'type': 'FLOAT64'},
        {'name': 'against_ice', 'type': 'FLOAT64'},
        {'name': 'against_fighting', 'type': 'FLOAT64'},
        {'name': 'against_poison', 'type': 'FLOAT64'},
        {'name': 'against_ground', 'type': 'FLOAT64'},
        {'name': 'against_flying', 'type': 'FLOAT64'},
        {'name': 'against_psychic', 'type': 'FLOAT64'},
        {'name': 'against_bug', 'type': 'FLOAT64'},
        {'name': 'against_rock', 'type': 'FLOAT64'},
        {'name': 'against_ghost', 'type': 'FLOAT64'},
        {'name': 'against_dragon', 'type': 'FLOAT64'},
        {'name': 'against_dark', 'type': 'FLOAT64'},
        {'name': 'against_steel', 'type': 'FLOAT64'},
        {'name': 'against_fairy', 'type': 'FLOAT64'},
        {'name': 'is_sublegendary', 'type': 'INT64'},
        {'name': 'is_legendary', 'type': 'INT64'},
        {'name': 'is_mythical', 'type': 'INT64'},
        {'name': 'description', 'type': 'STRING'},
        {'name': 'wins', 'type': 'INT64'},
        {'name': 'losses', 'type': 'INT64'},
        {'name': 'times_chosen', 'type': 'INT64'}])
    logger.info(f"Successfully loaded dataframe into '{dataset.dataset_id}'.")

load_to_gbq()