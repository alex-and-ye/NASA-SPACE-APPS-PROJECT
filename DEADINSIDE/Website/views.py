from django.shortcuts import render
import csv
from django.conf import settings
import os
import pandas as pd
import numpy as np
def process_exoplanet_data():
   # csv_file_path = os.path.join(settings.BASE_DIR, 'exoplanet_data.csv')
    
    # Read the CSV file, skipping the comment lines
    df = pd.read_csv('exoplanet_data.csv', comment='#')

    # Select only the columns we need
    columns_of_interest = ['pl_name', 'hostname', 'pl_orbsmax', 'pl_rade', 'st_rad', 'sy_dist']
    df_filtered = df[columns_of_interest]

    # Remove any rows with missing data
    df_filtered = df_filtered.dropna()

    # Calculate SNR
    D = 6  # Telescope diameter in meters
    snro = 100  # Reference SNR

    df_filtered['snr'] = snro * ((df_filtered['st_rad'] * df_filtered['pl_rade'] * D / 6) / 
                                 (df_filtered['sy_dist'] / 10 * df_filtered['pl_orbsmax']))**2

    # Convert DataFrame to dictionary for easy use in template
    exoplanets = df_filtered.to_dict('records')

    return {
        'exoplanets': exoplanets,
        'avg_snr': df_filtered['snr'].mean(),
        'max_snr': df_filtered['snr'].max(),
        'min_snr': df_filtered['snr'].min(),
    }

def home_page_view(request):
    template_name = 'website/home.html'
    
    exoplanet_data = process_exoplanet_data()
    
    context = {
        'user': request.user,
        'exoplanet_data': exoplanet_data,
    }
    return render(request, template_name, context)