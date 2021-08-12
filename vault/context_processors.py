from django.conf import settings


def vault_settings(request):
    return {
        'DEBUG': settings.DEBUG,
        'ENVIRON': settings.ENVIRON,
        'HELP_URL': settings.HELP_URL,
        'SWIFT_CLOUD_ENABLED': settings.SWIFT_CLOUD_ENABLED,
    }


def vault_session(request):
    return {
        'logged_user': request.user,
        'project_id': request.session.get('project_id'),
        'project_name': request.session.get('project_name'),
        'auth_token': request.session.get('auth_token'),
        'is_superuser': request.user.is_superuser,
    }
