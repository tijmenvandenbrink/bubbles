from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = 'report_type month year'
    help = 'Uploads availability/volume reports to VERS for a specific time period'

    def handle(self, *args, **options):
        # todo: Create a command that exports availability/volume data to VERS
        pass