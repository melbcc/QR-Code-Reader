from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Creates an administrator user."

    def add_arguments(self, parser):
        parser.add_argument('username', help="Admin user's username")
        parser.add_argument('password', help="Admin user's password")

    def handle(self, *args, **kwargs):
        user = User.objects.create_superuser(
            username=kwargs['username'],
            password=kwargs['password'],
        )
        print(f"user created: {user!r}")
