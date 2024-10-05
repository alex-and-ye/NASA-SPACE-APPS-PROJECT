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
    columns_of_interest = ['pl_name', 'hostname', 'pl_orbsmax', 'pl_rade', 'st_rad', 'sy_dist', 'pl_eqt']
    df_filtered = df[columns_of_interest]

    # Remove any rows with missing data
    df_filtered = df_filtered.dropna()

    # Calculate SNR
    snro = 100  # Reference SNR
    df_filtered['snr'] = snro * (((df_filtered['st_rad'] * df_filtered['pl_rade'] * telescope_diameter / 6) / 
                                 ((df_filtered['sy_dist'] / 10) * df_filtered['pl_orbsmax']))**2)

    # Apply filters
    df_filtered = df_filtered[df_filtered['snr'] > min_snr]
    df_filtered = df_filtered[df_filtered['sy_dist'] <= max_distance]

    if habitable_only:
        df_filtered = df_filtered[(df_filtered['pl_eqt'] >= 200) & (df_filtered['pl_eqt'] <= 300)]

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
        'df_filtered': df_filtered  # Add this line to return the filtered DataFrame
    }
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
    return render(request, template_name, context)

def get_planets(request):
    start = int(request.GET.get('start', 0))
    count = int(request.GET.get('count', 6))
    
    # Get filter parameters from the request
    telescope_diameter = float(request.GET.get('telescope_diameter', 6))
    min_snr = float(request.GET.get('min_snr', 5))
    habitable_only = request.GET.get('habitable_only', 'off') == 'on'
    max_distance = float(request.GET.get('max_distance', 1000))

    # Process the exoplanet data with the given filters
    exoplanet_data = process_exoplanet_data(request)
    df_filtered = exoplanet_data['df_filtered']
    
    # Get the requested slice of planets
    planets = df_filtered.iloc[start:start+count].to_dict('records')
    
    return JsonResponse({'planets': planets})