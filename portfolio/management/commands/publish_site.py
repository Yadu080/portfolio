from django.core.management.base import BaseCommand, CommandError

from portfolio import publish


class Command(BaseCommand):
    help = "Build the static site and push it to GitHub Pages (same as the studio's Publish button)."

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS(publish.publish()))
        except publish.PublishError as exc:
            raise CommandError(str(exc)) from exc
