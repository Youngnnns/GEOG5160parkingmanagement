import csv
from django.core.management.base import BaseCommand
from parking.models import PublicParkingPricingModel1, PublicParkingPricingModel2, PublicParkingPricingModel3, \
    PublicParkingPricingModel4


class Command(BaseCommand):
    help = 'Import parking pricing data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('pricing_model1_csv', type=str, help='Path to the pricing model 1 CSV file')
        parser.add_argument('pricing_model2_csv', type=str, help='Path to the pricing model 2 CSV file')
        parser.add_argument('pricing_model3_csv', type=str, help='Path to the pricing model 3 CSV file')
        parser.add_argument('pricing_model4_csv', type=str, help='Path to the pricing model 4 CSV file')

    def handle(self, *args, **options):
        self.import_pricing_model(options['pricing_model1_csv'], PublicParkingPricingModel1,
                                  self.pricing_model1_fields())
        self.import_pricing_model(options['pricing_model2_csv'], PublicParkingPricingModel2,
                                  self.pricing_model2_fields())
        self.import_pricing_model(options['pricing_model3_csv'], PublicParkingPricingModel3,
                                  self.pricing_model3_fields())
        self.import_pricing_model(options['pricing_model4_csv'], PublicParkingPricingModel4,
                                  self.pricing_model4_fields())
        self.stdout.write(self.style.SUCCESS('Successfully imported all pricing data'))

    def pricing_model1_fields(self):
        return ['OBJECTID', 'parking_name', 'day_of_week', 'start_time', 'end_time', 'price', 'fixed']

    def pricing_model2_fields(self):
        return ['OBJECTID', 'parking_name', 'period_type', 'start_time', 'end_time', 'duration_hours', 'price']

    def pricing_model3_fields(self):
        return ['OBJECTID', 'parking_name', 'day_of_week', 'duration_hours', 'price']

    def pricing_model4_fields(self):
        return ['OBJECTID', 'parking_name', 'day_of_week', 'duration_hours', 'price']

    def import_pricing_model(self, csv_file, model, fields):
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                obj = model(**{field: row.get(field) for field in fields})
                obj.save()
