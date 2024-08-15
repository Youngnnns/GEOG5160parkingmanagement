import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from parking.models import ParkingLot


class Command(BaseCommand):
    help = 'Import parking lot data from GeoJSON files'

    def handle(self, *args, **options):
        self.import_parking_lot('PD1.geojson')
        self.import_parking_lot('CCParking.geojson')
        self.stdout.write(self.style.SUCCESS('Successfully imported all parking lot data'))

    def import_parking_lot(self, geojson_file):
        with open(geojson_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for feature in data['features']:
                properties = feature['properties']
                geometry = GEOSGeometry(json.dumps(feature['geometry']))
                lot_type = properties['lot_type']

                if lot_type == 'roadside':
                    obj = ParkingLot(
                        OBJECTID=properties['OBJECTID'],
                        street_name=properties['Street Name'],
                        address=properties['Address'],
                        capacity=properties['Capacity'],
                        available_spaces=properties['Capacity'],  # Assuming all spaces are available initially
                        maximum_stay=properties['Maximum Stay'],
                        charges=properties['Electric or hydrogen or hybrid'],  # Assuming the same structure for charges
                        electric_or_hydrogen_or_hybrid=properties['Electric or hydrogen or hybrid'],
                        petrol_vehicles_registered_from_2005=properties['Petrol vehicles registered from 2005'],
                        diesel_vehicles_registered_from_2015=properties['Diesel vehicles registered from 2015'],
                        other_vehicles=properties['Other vehicles'],
                        saturday_am_price=properties['Saturday am price'],
                        lot_type=lot_type,
                        location=geometry
                    )
                elif lot_type == 'public':
                    obj = ParkingLot(
                        OBJECTID=properties['OBJECTID'],
                        car_park_name=properties['Car Park Name'],
                        address=properties['Address'],
                        capacity=properties['Capacity'],
                        available_spaces=properties['Capacity'],  # Assuming all spaces are available initially
                        charges=properties['Charges'],
                        postcode=properties['Postcode'],
                        lot_type=lot_type,
                        location=geometry
                    )
                obj.save()
