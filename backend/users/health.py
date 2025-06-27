from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json
import redis
from django.conf import settings

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for production monitoring
    """
    health_status = {
        'status': 'healthy',
        'timestamp': 'now',
        'services': {}
    }
    
    overall_healthy = True
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        overall_healthy = False
    
    # Check Redis connectivity (if configured)
    try:
        import redis
        r = redis.Redis.from_url(getattr(settings, 'REDIS_URL', 'redis://redis:6379/1'))
        r.ping()
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        overall_healthy = False
    
    # Check disk space
    import shutil
    try:
        disk_usage = shutil.disk_usage('/')
        free_space_gb = disk_usage.free / (1024**3)
        if free_space_gb > 1:  # At least 1GB free
            health_status['services']['disk_space'] = f'healthy ({free_space_gb:.1f}GB free)'
        else:
            health_status['services']['disk_space'] = f'warning ({free_space_gb:.1f}GB free)'
            if free_space_gb < 0.5:
                overall_healthy = False
    except Exception as e:
        health_status['services']['disk_space'] = f'error: {str(e)}'
    
    if not overall_healthy:
        health_status['status'] = 'unhealthy'
        return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status, status=200)
