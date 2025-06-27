from django.core.management.base import BaseCommand
from users.models import APIKey
from django.utils import timezone


class Command(BaseCommand):
    help = 'List all API keys'

    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active API keys'
        )

    def handle(self, *args, **options):
        queryset = APIKey.objects.all()
        
        if options['active_only']:
            queryset = queryset.filter(is_active=True)
        
        self.stdout.write(self.style.SUCCESS('API Keys:'))
        self.stdout.write('-' * 80)
        
        for api_key in queryset:
            status_indicator = '✓' if api_key.is_active else '✗'
            last_used = api_key.last_used.strftime('%Y-%m-%d %H:%M') if api_key.last_used else 'Never'
            
            self.stdout.write(f'{status_indicator} {api_key.key_name}')
            self.stdout.write(f'   Prefix: {api_key.key_prefix}...')
            self.stdout.write(f'   Created: {api_key.created_at.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'   Last Used: {last_used}')
            self.stdout.write(f'   Rate Limit: {api_key.rate_limit}/hour')
            self.stdout.write(f'   Permissions: {api_key.permissions}')
            
            if api_key.expires_at:
                expires = api_key.expires_at.strftime('%Y-%m-%d %H:%M')
                if api_key.expires_at < timezone.now():
                    self.stdout.write(f'   Expires: {expires} (EXPIRED)')
                else:
                    self.stdout.write(f'   Expires: {expires}')
            else:
                self.stdout.write('   Expires: Never')
            
            self.stdout.write('')
