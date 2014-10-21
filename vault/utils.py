# -*- coding:utf-8 -*-

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def update_default_context(request, context={}):

    context['logged_user'] = request.user
    context['logout_url'] = settings.LOGOUT_URL

    if not request.session.get('project_id'):
        request.session['project_id'] = request.user.project_id

    context['project_id'] = request.session.get('project_id')

    if not request.session.get('has_identity'):
        request.session['has_identity'] = request.user.is_superuser

    context['has_identity'] = request.session.get('has_identity')

    return context

def generic_pagination(items, page=1, per_page=2):

    paginator = Paginator(items, per_page) # Show 5 items per page

    try:
        paginated_items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_items = paginator.page(paginator.num_pages)

    return paginated_items
