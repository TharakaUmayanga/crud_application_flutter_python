from django.core.management.base import BaseCommand
from users.models import APIKey


class Command(BaseCommand):
    help = 'Generate a new API key'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Name for the API key'
        )
        parser.add_argument(
            '--permissions',
            type=str,
            default='users:read,write',
            help='Permissions in format "resource:action1,action2;resource2:action1"'
        )
        parser.add_argument(
            '--rate-limit',
            type=int,
            default=1000,
            help='Rate limit per hour (default: 1000)'
        )

    def handle(self, *args, **options):
        name = options['name']
        rate_limit = options['rate_limit']
        
        # Parse permissions
        permissions = {}
        if options['permissions']:
            for perm_group in options['permissions'].split(';'):
                if ':' in perm_group:
                    resource, actions = perm_group.split(':', 1)
                    permissions[resource.strip()] = [action.strip() for action in actions.split(',')]
        
        if not permissions:
            permissions = {'users': ['read', 'write']}
        
        try:
            api_key_obj, key = APIKey.generate_key(
                name=name,
                permissions=permissions,
                rate_limit=rate_limit
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created API key: {name}')
            )
            self.stdout.write(f'API Key: {key}')
            self.stdout.write(f'Prefix: {api_key_obj.key_prefix}')
            self.stdout.write(f'Permissions: {permissions}')
            self.stdout.write(f'Rate Limit: {rate_limit} requests/hour')
            self.stdout.write(
                self.style.WARNING('Save this key securely - it will not be shown again!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating API key: {str(e)}')
            )
