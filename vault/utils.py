# -*- coding:utf-8 -*-

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def update_default_context(request, context={}):

    if not request.session.get('is_superuser'):
        request.session['is_superuser'] = request.user.is_superuser

    context.update({
        'logged_user': request.user,
        'logout_url': settings.LOGOUT_URL,
        'project_id': request.session.get('project_id'),
        'project_name': request.session.get('project_name'),
        'is_superuser': request.user.is_superuser,
    })

    return context


def generic_pagination(items, page=1, per_page=settings.PAGINATION_SIZE):

    paginator = Paginator(items, per_page)

    try:
        paginated_items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_items = paginator.page(paginator.num_pages)

    return paginated_items
