from django.shortcuts import render
import csv
from django.conf import settings
import os
import pandas as pd
import numpy as np

def process_exoplanet_data():
    csv_file_path = os.path.join(settings.BASE_DIR, 'exoplanet_data.csv')
    
    # Read the CSV file, skipping the comment lines
    df = pd.read_csv(csv_file_path, comment='#')

    # Select only the columns we need
    columns_of_interest = ['pl_name', 'hostname', 'pl_orbper', 'pl_orbsmax', 'pl_rade', 'st_rad', 'sy_dist']
    df_filtered = df[columns_of_interest]

    # Remove any rows with missing data
    df_filtered = df_filtered.dropna()

    # Convert DataFrame to dictionary for easy use in template
    exoplanets = df_filtered.to_dict('records')

    # Calculate some basic statistics
    orbital_period = df_filtered['pl_orbper']
    semi_major_axis = df_filtered['pl_orbsmax']
    planet_radius = df_filtered['pl_rade']
    star_radius = df_filtered['st_rad']
    distance = df_filtered['sy_dist']
    snro = 100
    snr = 
    return {
        'exoplanets': exoplanets,
        'stats': {
            'avg_orbital_period': avg_orbital_period,
            'avg_semi_major_axis': avg_semi_major_axis,
            'avg_planet_radius': avg_planet_radius,
            'avg_star_radius': avg_star_radius,
            'avg_distance': avg_distance,
        }
    }

def home_page_view(request):
    template_name = 'website/home.html'
    
    exoplanet_data = process_exoplanet_data()
    
    context = {
        'user': request.user,
        'exoplanet_data': exoplanet_data,
    }
    return render(request, template_name, context)