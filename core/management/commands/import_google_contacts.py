import os

import gspread
from django.core.management.base import BaseCommand, CommandError

from core.contact_importer import import_contact_rows, validate_headers


class Command(BaseCommand):
    help = "Import contacts from a Google Sheet."

    def add_arguments(self, parser):
        parser.add_argument("sheet_url", type=str)

    def handle(self, *args, **options):
        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

        if not service_account_file:
            raise CommandError(
                "GOOGLE_SERVICE_ACCOUNT_FILE is not set in your environment."
            )

        sheet_url = options["sheet_url"]

        try:
            client = gspread.service_account(filename=service_account_file)
            spreadsheet = client.open_by_url(sheet_url)
            worksheet = spreadsheet.sheet1
            rows = worksheet.get_all_records()
        except Exception as error:
            raise CommandError(f"Could not read Google Sheet: {error}")

        if not rows:
            raise CommandError("Google Sheet has no data rows.")

        headers = list(rows[0].keys())

        try:
            validate_headers(headers)
        except ValueError as error:
            raise CommandError(str(error))

        result = import_contact_rows(rows)

        self.stdout.write(
            self.style.SUCCESS(
                f"Google import complete. Created: {result['created']}, "
                f"Updated: {result['updated']}, Skipped: {result['skipped']}"
            )
        )