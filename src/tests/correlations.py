import os
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import seaborn as sns
import matplotlib.pyplot as plt
import concurrent.futures
import argparse


# Function to clean and preprocess Achilles data
def clean_achilles_data(data):
    # Drop rows with missing values
    data = data.dropna()
    
    # Replace spaces and remove parentheses from column names
    data.columns = data.columns.str.replace(" ", "_").str.replace("[()]", "", regex=True)
    
    # Melt the DataFrame
    data_clean = pd.melt(data, id_vars=["DepMap_ID"], var_name="genes", value_name="value_gene_selected")
    data_clean[['gene', 'gene_id']] = data_clean['genes'].str.split('_', expand=True)
    data_clean.drop(columns=['genes'], inplace = True)
    return data_clean

# Function to clean and preprocess the map data
def clean_map_data(map_data):
    # Split and extract relevant information
    map_data[['chromosome', 'avg_pos', '_']] = map_data['genome_alignment'].str.split('_', expand=True)
    map_data[['gene', 'gene_id']] = map_data['gene'].str.split(' ', expand=True)
    map_data['gene_id'] = map_data['gene_id'].str.replace("[()]", "", regex=True)
    
    return map_data


# correlations for a single gene
def calculate_gene_correlations(other_gene):
    other_gene_data = data[data['gene'] == other_gene]['value_gene_selected']
    correlation, pvalue =  pearsonr(selected_gene_data, other_gene_data)
    return {'SELECTED_GENE': GENE_SELECTED, 'EVALUATED_GENE': other_gene, 'CORRELATION': correlation, 'PVALUE': pvalue, 'LOGPVALUE': -np.log10(pvalue)}



if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Calculate gene correlations.')
    parser.add_argument('GENE_SELECTED', type=str, help='The selected gene name')
    parser.add_argument('--map_file', type=str, default='../data/22Q2/Achilles_guide_map.csv', help='Path to the map file')
    parser.add_argument('--data_file', type=str, default='../data/22Q2/Achilles_gene_effect.csv', help='Path to the data file')
    args = parser.parse_args()

    GENE_SELECTED = args.GENE_SELECTED

    # Call functions to perform data processing
    map_file = args.map_file
    data_file = args.data_file

    # Read data 
    map_data = pd.read_csv(map_file)
    achilles_data = pd.read_csv(data_file)

    # Call functions to perform data processing
    achilles_clean = clean_achilles_data(achilles_data)
    map_clean = clean_map_data(map_data)
    

    # Compute correlations
    data = achilles_clean.copy()
    unique_genes = data['gene'].unique()
    selected_gene_data = data[data['gene'] == GENE_SELECTED]['value_gene_selected']
    correlations = []
    print("Starting to compute gene dependency for " + GENE_SELECTED)
    # concurrent.futures to parallelize the computation
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for gene_count, result in enumerate(executor.map(calculate_gene_correlations, unique_genes), 1):
            correlations.append(result)
            
            # Print progress 
            if gene_count % 1000 == 0:
                print(f"Computed correlations for {gene_count} / {len(unique_genes)} genes.")

    # Save the results to a CSV file    
    FILENAME = "../output/correlations/correlations_" + GENE_SELECTED + "_by_chr.csv"
    # Save the results to a CSV file
    correlations.to_csv(FILENAME, index=False)
