from django.shortcuts import render
import csv
from django.conf import settings
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import io
import base64
from django.http import JsonResponse
from django.template.loader import render_to_string

def home_page_view(request):
    template_name = 'website/home.html'
    
    exoplanet_data = process_exoplanet_data(request)
    
    context = {
        'user': request.user,
        'exoplanet_data': exoplanet_data,
        'filters': {
            'telescope_diameter': request.GET.get('telescope_diameter', 6),
            'min_snr': request.GET.get('min_snr', 5),
            'habitable_only': request.GET.get('habitable_only', 'off'),
            'max_distance': request.GET.get('max_distance', 1000),
        }
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'planets': exoplanet_data['exoplanets'],
            'total_planets': exoplanet_data['total_planets'],
            'avg_snr': exoplanet_data['avg_snr'],
            'median_snr': exoplanet_data['median_snr'],
            'std_snr': exoplanet_data['std_snr'],
            'max_snr': exoplanet_data['max_snr'],
            'min_snr': exoplanet_data['min_snr'],
        })
    
    return render(request, template_name, context)
def process_exoplanet_data(request):
    csv_file_path = os.path.join(os.path.dirname(__file__), 'exoplanet_data.csv')
    
    # Read the CSV file, skipping the comment lines
    df = pd.read_csv(csv_file_path, comment='#')

    # Get filter parameters from the request
    telescope_diameter = float(request.GET.get('telescope_diameter', 6))
    min_snr = float(request.GET.get('min_snr', 5))
    habitable_only = request.GET.get('habitable_only', 'off') == 'on'
    max_distance = float(request.GET.get('max_distance', 1000))

    # Select only the columns we need
    columns_of_interest = ['pl_name', 'hostname', 'pl_orbsmax', 'pl_rade', 'st_rad', 'sy_dist', 'pl_eqt', 
                           'pl_bmasse', 'st_spectype', 'st_mass', 'st_teff']
    df_filtered = df[columns_of_interest]

    # Remove any rows with missing data
    df_filtered = df_filtered.dropna()

    # Calculate SNR
    snro = 100  # Reference SNR
    df_filtered['snr'] = snro * (((df_filtered['st_rad'] * df_filtered['pl_rade'] * telescope_diameter / 6) / 
                                 ((df_filtered['sy_dist'] / 10) * df_filtered['pl_orbsmax']))**2)

    # Calculate Magnetic Field potential
    df_filtered['B'] = df_filtered['pl_bmasse'] / (df_filtered['pl_rade'] ** 3)

    # Determine star type and habitable zone
    def get_star_type_and_hz(row):
        if row['st_teff'] > 5200 and row['st_teff'] <= 6000:
            return 'G', 0.95, 1.37
        elif row['st_teff'] > 3700 and row['st_teff'] <= 5200:
            return 'K', 0.5, 1.0
        elif row['st_teff'] <= 3700:
            return 'M', 0.03, 0.5
        else:
            return 'Other', np.nan, np.nan

    df_filtered[['star_type', 'hz_inner', 'hz_outer']] = df_filtered.apply(get_star_type_and_hz, axis=1, result_type='expand')

    # Determine if planet is in habitable zone
    df_filtered['in_habitable_zone'] = (
        (df_filtered['pl_orbsmax'] >= df_filtered['hz_inner']) & 
        (df_filtered['pl_orbsmax'] <= df_filtered['hz_outer'])
    )

    df_filtered = df_filtered[df_filtered['snr'] > min_snr]
    df_filtered = df_filtered[df_filtered['sy_dist'] <= max_distance]

    if habitable_only:
        df_filtered = df_filtered[
            (df_filtered['pl_eqt'] >= 200) & (df_filtered['pl_eqt'] <= 300) &
            (df_filtered['B'] >= 25) & (df_filtered['B'] <= 65) &
            df_filtered['in_habitable_zone']
        ]

    # Keep only the middle 95% of the data
    lower_percentile = df_filtered['snr'].quantile(0.025)
    upper_percentile = df_filtered['snr'].quantile(0.975)
    df_filtered = df_filtered[(df_filtered['snr'] >= lower_percentile) & (df_filtered['snr'] <= upper_percentile)]

    # Sort planets by distance
    df_filtered = df_filtered.sort_values('sy_dist')

    # Select the 6 closest planets
    closest_planets = df_filtered.head(6).to_dict('records')

    # Calculate statistics
    snr_mean = df_filtered['snr'].mean()
    snr_std = df_filtered['snr'].std()
    snr_median = df_filtered['snr'].median()

    # Convert DataFrame to dictionary for easy use in template
    exoplanets = df_filtered.to_dict('records')

    return {
    'exoplanets': exoplanets,
    'closest_planets': closest_planets,
    'avg_snr': snr_mean,
    'median_snr': snr_median,
    'std_snr': snr_std,
    'max_snr': df_filtered['snr'].max(),
    'min_snr': df_filtered['snr'].min(),  # Changed from 'min_snr' to 'snr'
    'total_planets': len(exoplanets),
    'df_filtered': df_filtered
}
def get_planets(request):
    exoplanet_data = process_exoplanet_data(request)
    
    return JsonResponse({
        'planets': exoplanet_data['exoplanets'],
        'total_planets': exoplanet_data['total_planets'],
        'avg_snr': exoplanet_data['avg_snr'],
        'median_snr': exoplanet_data['median_snr'],
        'std_snr': exoplanet_data['std_snr'],
        'max_snr': exoplanet_data['max_snr'],
        'min_snr': exoplanet_data['min_snr'],
    })