from django.apps import AppConfig


class ParkingConfig(AppConfig):
    name = 'parking'

    def ready(self):
        from . import tasks  # Ensure that the scheduler is properly imported from your module using the
        tasks.start()  # Start the scheduler
