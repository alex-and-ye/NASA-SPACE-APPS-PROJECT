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
    columns_of_interest = ['pl_name', 'hostname', 'pl_orbsmax', 'pl_rade', 'st_rad', 'sy_dist', 'pl_eqt', 'st_teff', 'pl_bmasse']
    df_filtered = df[columns_of_interest]

    # Remove any rows with missing data
    df_filtered = df_filtered.dropna()

    # Calculate SNR
    snro = 100  # Reference SNR
    df_filtered['snr'] = snro * (((df_filtered['st_rad'] * df_filtered['pl_rade'] * telescope_diameter / 6) / 
                                 ((df_filtered['sy_dist'] / 10) * df_filtered['pl_orbsmax']))**2)

    # Calculate Magnetic Field potential
    df_filtered['B'] = df_filtered['pl_bmasse'] / (df_filtered['pl_rade'] ** 3)

    # Calculate habitable zone
    def get_habitable_zone(star_temp):
        if star_temp > 5200 and star_temp <= 6000:  # G-type star
            return 0.95, 1.37
        elif star_temp > 3700 and star_temp <= 5200:  # K-type star
            return 0.5, 1.0
        elif star_temp <= 3700:  # M-type star
            return 0.03, 0.5
        else:
            return None, None

    df_filtered['hz_inner'], df_filtered['hz_outer'] = zip(*df_filtered['st_teff'].apply(get_habitable_zone))
    df_filtered['in_habitable_zone'] = (df_filtered['pl_orbsmax'] >= df_filtered['hz_inner']) &  (df_filtered['pl_orbsmax'] <= df_filtered['hz_outer'])

    # Apply filters
    df_filtered = df_filtered[df_filtered['snr'] > min_snr]
    df_filtered = df_filtered[df_filtered['sy_dist'] <= max_distance]

    if habitable_only:
        df_filtered = df_filtered[
            df_filtered['in_habitable_zone'] &
            (df_filtered['pl_eqt'] >= 200) & (df_filtered['pl_eqt'] <= 300) &
            (df_filtered['B'] >= 25) & (df_filtered['B'] <= 65)
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

    # Create histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df_filtered['snr'], bins=50, edgecolor='black')
    plt.title('Distribution of SNR Values (Middle 95%)')
    plt.xlabel('SNR')
    plt.ylabel('Frequency')
    plt.axvline(snr_mean, color='red', linestyle='dashed', linewidth=2, label=f'Mean ({snr_mean:.2f})')
    plt.axvline(snr_median, color='green', linestyle='dashed', linewidth=2, label=f'Median ({snr_median:.2f})')
    plt.legend()
    
    # Save histogram to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    histogram_image = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    # Create box plot
    plt.figure(figsize=(10, 6))
    plt.boxplot(df_filtered['snr'])
    plt.title('Box Plot of SNR Values (Middle 95%)')
    plt.ylabel('SNR')
    
    # Save box plot to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    boxplot_image = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    # Convert DataFrame to dictionary for easy use in template
    exoplanets = df_filtered.to_dict('records')

    return {
        'exoplanets': exoplanets,
        'closest_planets': closest_planets,
        'avg_snr': snr_mean,
        'median_snr': snr_median,
        'std_snr': snr_std,
        'max_snr': df_filtered['snr'].max(),
        'min_snr': df_filtered['snr'].min(),
        'histogram_image': histogram_image,
        'boxplot_image': boxplot_image,
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