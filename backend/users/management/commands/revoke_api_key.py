from django.core.management.base import BaseCommand
from users.models import APIKey


class Command(BaseCommand):
    help = 'Revoke (deactivate) an API key'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefix',
            type=str,
            required=True,
            help='Prefix of the API key to revoke'
        )

    def handle(self, *args, **options):
        prefix = options['prefix']
        
        try:
            api_key = APIKey.objects.get(key_prefix=prefix)
            
            if not api_key.is_active:
                self.stdout.write(
                    self.style.WARNING(f'API key "{api_key.key_name}" is already inactive')
                )
                return
            
            api_key.is_active = False
            api_key.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully revoked API key: {api_key.key_name}')
            )
            
        except APIKey.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'API key with prefix "{prefix}" not found')
            )
