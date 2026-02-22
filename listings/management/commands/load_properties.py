"""
Management command to load properties from Future_Trend_Dataset_100K.xlsx
into the Property model.

Usage:
    python manage.py load_properties              # load all 100K rows
    python manage.py load_properties --limit 500  # load first 500 rows
    python manage.py load_properties --clear       # delete existing then load
"""
import os
from django.core.management.base import BaseCommand
from listings.models import Property

try:
    import pandas as pd
except ImportError:
    pd = None


class Command(BaseCommand):
    help = 'Load property data from Future_Trend_Dataset_100K.xlsx'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=None,
            help='Maximum number of rows to import (default: all)'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete all existing properties before importing'
        )
        parser.add_argument(
            '--file', type=str, default='Future_Trend_Dataset_100K.xlsx',
            help='Path to the Excel file (default: Future_Trend_Dataset_100K.xlsx)'
        )

    def handle(self, *args, **options):
        if pd is None:
            self.stderr.write(self.style.ERROR(
                'pandas is required. Install with: pip install pandas openpyxl'
            ))
            return

        file_path = options['file']
        if not os.path.isabs(file_path):
            from django.conf import settings
            file_path = os.path.join(settings.BASE_DIR, file_path)

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        if options['clear']:
            deleted, _ = Property.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing properties.'))

        self.stdout.write(f'Reading {file_path}...')
        nrows = options['limit']
        df = pd.read_excel(file_path, nrows=nrows)
        self.stdout.write(f'Read {len(df)} rows. Importing...')

        batch_size = 5000
        properties = []

        for idx, row in df.iterrows():
            prop = Property(
                city=row['City'],
                area=row['Area'],
                property_type=row['Property_Type'],
                size_sqft=int(row['Size_sqft']),
                bedrooms=int(row['Bedrooms']),
                age_of_property_years=int(row['Age_of_Property_years']),
                nearby_infrastructure_score=int(row['Nearby_Infrastructure_Score']),
                distance_to_city_center_km=float(row['Distance_to_City_Center_km']),
                year=int(row['Year']),
                price_inr=int(row['Price_INR']),
                title=f"{row['Property_Type']} in {row['Area']}, {row['City']}",
            )
            properties.append(prop)

            if len(properties) >= batch_size:
                Property.objects.bulk_create(properties)
                self.stdout.write(f'  Imported {idx + 1} rows...')
                properties = []

        # Insert remaining
        if properties:
            Property.objects.bulk_create(properties)

        total = Property.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Done! Imported {len(df)} rows. Total properties in DB: {total}'
        ))
