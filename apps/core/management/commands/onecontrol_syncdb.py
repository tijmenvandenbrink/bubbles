from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = 'report_type month year'
    help = 'Fetches data from OneControl and imports it into the Bubbles database'

    def handle(self, *args, **options):
        # todo: Create a command that fetches Event data from OneControl for availability calculations
        # todo: Create a command that fetches Performance data from OneControl for performance statistics
        pass
