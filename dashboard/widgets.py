
from django.conf import settings
from django.template.loader import render_to_string


class BaseWidget(object):
    title = 'Widget Title'
    subtitle = 'Widget Subtitle'
    description = 'Widget Description'
    content_template = 'dashboard/widgets/content.html'
    non_renderable_template = 'dashboard/widgets/non_renderable.html'

    def __init__(self, context):
        self.context = context

    def get_widget_context(self):
        return {}

    def _full_context(self):
        widget_context = self.get_widget_context()
        widget_context.update({
            'title': self.title,
            'subtitle': self.subtitle if self.subtitle != '' else self.title,
            'description': self.description,
            'content_template': self.content_template
        })
        return widget_context

    def render(self):
        return render_to_string(self._get_widget_template(),
                                self._full_context())

    @property
    def renderable(self):
        return True

    def _get_widget_template(self):
        if self.renderable:
            return 'dashboard/widgets/full.html'
        else:
            return self.non_renderable_template


# def _widget_users(self):
    #     users = []

    #     try:
    #         users = self.keystone.user_list()
    #     except exceptions.Forbidden:
    #         return False
    #     except Exception as e:
    #         log.exception('Exception: %s' % e)
    #         messages.add_message(self.request, messages.ERROR,
    #                              "Error getting user list")
    #     return {
    #         'total_users': len(users),
    #         'url': reverse('users')
    #     }

    # def _widget_storage(self):
    #     storage_url = get_admin_url(self.request)
    #     auth_token = get_token_id(request)
    #     http_conn = client.http_connection(storage_url,
    #                                        insecure=settings.SWIFT_INSECURE)
    #     try:
    #         account_stat, containers = client.get_account(storage_url,
    #                                                       auth_token,
    #                                                       http_conn=http_conn)
    #     except client.ClientException as err:
    #         log.exception('Exception: {0}'.format(err))
    #         return False
    #         # TODO - Handle user without permission
    #         # messages.add_message(self.request, messages.ERROR,
    #         #                     'Unable to list containers')
    #         containers = []

    #     objects = 0
    #     size = 0

    #     for container in containers:
    #         objects += container['count']
    #         size += container['bytes']

    #     return {
    #         'containers': len(containers),
    #         'objects': objects,
    #         'size': size,
    #         'url': reverse('containerview')
    #     }
