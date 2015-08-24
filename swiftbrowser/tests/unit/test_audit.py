# -*- coding:utf-8 -*-

import mock

from mock import patch
from unittest import TestCase

from swiftbrowser.tests import fakes
from swiftbrowser import views

from vault.tests.fakes import fake_request
import datetime


class TestSwiftbrowserAudit(TestCase):

    def setUp(self):

        self.user = fakes.FakeUser(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated = lambda: True

        self.request = fake_request(user=self.user)
        self.request.session['project_id'] = 'fakeid'

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('swiftbrowser.views.Audit').start()

        # ACTIONS
        self.mock_audit_save.ADD = 'Cadastrou'
        self.mock_audit_save.UPDATE = 'Atualizou / Editou'
        self.mock_audit_save.DELETE = 'Removeu'
        self.mock_audit_save.LIST = 'Listou / Visualizou'
        self.mock_audit_save.UPLOAD = 'Realizou upload'
        self.mock_audit_save.DOWNLOAD = 'Realizou Download'
        self.mock_audit_save.ENABLE = 'Habilitou'
        self.mock_audit_save.DISABLE = 'Desabilitou'
        self.mock_audit_save.SWITCH = 'Alternou'

        # THROUGHTS and MODULES
        self.mock_audit_save.VAULT = 'Vault'
        self.mock_audit_save.DASHBOARD = 'Dashboard'
        self.mock_audit_save.IDENTITY = 'Identity'
        self.mock_audit_save.SWIFTBROWSER = 'SwiftBrowser'
        self.mock_audit_save.DJANGO = 'Django'
        self.mock_audit_save.VAULT_IDENTITY = 'Vault - Identity'
        self.mock_audit_save.VAULT_SWIFTBROWSER = 'Vault - SwiftBrowser'

        # ITENS
        self.mock_audit_save.USERS = 'Usuarios'
        self.mock_audit_save.USER = 'Usuario'
        self.mock_audit_save.PROJECTS = 'Projetos'
        self.mock_audit_save.PROJECT = 'Projeto'
        self.mock_audit_save.AREAS = 'Areas'
        self.mock_audit_save.AREA = 'Area'
        self.mock_audit_save.TEAMS = 'Times'
        self.mock_audit_save.TEAMS = 'Time'
        self.mock_audit_save.USER_ROLES = 'Usuario e Permissionamento'
        self.mock_audit_save.CONTAINERS = 'Containers'
        self.mock_audit_save.CONTAINER = 'Container'
        self.mock_audit_save.OBJECTS = 'Objectos'
        self.mock_audit_save.OBJECT = 'Objeto'
        self.mock_audit_save.PSEUDO_FOLDER = 'PseudoFolder'
        self.mock_audit_save.ACL = 'ACL'
        self.mock_audit_save.METADATA = 'Metadado'
        self.mock_audit_save.VERSIONING = 'Versionamento'

        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    @patch('swiftbrowser.views.client.get_account')
    def test_list_containerview_call_audit(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        views.containerview(self.request)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.LIST, item=self.mock_audit_save.CONTAINERS, through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.put_container')
    def test_create_container_valid_form_call_audit(self, mock_put_container):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'containername': 'fakecontainer'})
        self.request.POST = post

        views.create_container(self.request)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.ADD, item=self.mock_audit_save.CONTAINER + ' - fakecontainer', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.requests.put')
    def test_create_object_status_201_call_audit(self, mock_requests_put):
        mock_requests_put.return_value = fakes.FakeRequestResponse(201)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        fakecontainer = 'fakecontainer'
        views.create_object(self.request, fakecontainer)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.ADD, item=self.mock_audit_save.OBJECT + ' - foo.txt', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.head_container')
    def test_edit_acl_list_acls_container_private_call_audit(self, mock_get_container):

        mock_get_container.return_value = {
            'x-container-read': '',
            'x-container-write': '',
        }

        views.edit_acl(self.request, 'fakecontainer')

        # audit = Audit(user=request.user.username, action=Audit.UPDATE, item=Audit.ACL + ' - ' + container, through=Audit.VAULT + ' - ' + Audit.SWIFTBROWSER, created_at=Audit.NOW)
        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.UPDATE, item=self.mock_audit_save.ACL + ' - fakecontainer', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
    def test_edit_acl_delete_acl_for_user_in_a_public_container_call_audit(self, mock_head_container, mock_post_container):

        mock_head_container.return_value = {
            'x-container-read': '.r:*,projectfake:userfake',
            'x-container-write': 'projectfake:userfake,projectfake2:userfake2',
        }

        self.request.method = 'GET'
        get = self.request.GET.copy()

        get.update({'delete': 'projectfake:userfake'})
        self.request.GET = get

        views.edit_acl(self.request, 'fakecontainer')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.UPDATE, item=self.mock_audit_save.ACL + ' - fakecontainer', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.put_object')
    def test_create_pseudofolder_with_no_prefix_call_audit(self, mock_put_object):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'foldername': 'fakepseudofolder'})
        self.request.POST = post

        views.create_pseudofolder(self.request, 'fakecontainer')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.ADD, item=self.mock_audit_save.PSEUDO_FOLDER + ' - fakepseudofolder', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.put_object')
    def test_create_pseudofolder_without_no_prefix_call_audit(self, mock_put_object):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'foldername': 'fakepseudofolder'})
        self.request.POST = post

        views.create_pseudofolder(self.request, 'fakecontainer')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.ADD, item=self.mock_audit_save.PSEUDO_FOLDER + ' - fakepseudofolder', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.delete_container')
    def test_delete_container_view_deletes_with_success_call_audit(self, mock_delete_container):

        mock_delete_container.return_value = True
        views.delete_container_view(self.request, container='container')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DELETE, item=self.mock_audit_save.CONTAINER + ' - container', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.delete_object')
    def test_delete_object_call_audit(self, mock_delete_object):

        fakecontainer = 'fakecontainer'
        fakeobject = 'fakeobject'

        views.delete_object(self.request, fakecontainer, fakeobject)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DELETE, item=self.mock_audit_save.OBJECT + ' - fakeobject', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.delete_object')
    def test_view_delete_object_inside_a_container_call_audit(self, mock_delete_object):

        mock_delete_object.return_value = True

        fakecontainer = 'fakecontainer'
        fakeobject_name = 'fakeobject'

        views.delete_object_view(self.request, fakecontainer, fakeobject_name)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DELETE, item=self.mock_audit_save.OBJECT + ' - fakeobject', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.delete_object')
    def test_view_delete_object_inside_a_pseudofolder_call_audit(self, mock_delete_object):

        mock_delete_object.return_value = True

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'
        fakeobject_name = fakepseudofolder + 'fakeobject'

        views.delete_object_view(self.request, fakecontainer, fakeobject_name)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DELETE, item=self.mock_audit_save.OBJECT + ' - fakepseudofolder/fakeobject', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.delete_object')
    @patch('swiftbrowser.views.client.get_container')
    def test_delete_empty_pseudofolder_call_audit(self, mock_get_container, mock_delete_object):

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'

        mock_get_container.return_value = ['stats', [{'name': fakepseudofolder}]]

        views.delete_pseudofolder(self.request, fakecontainer, fakepseudofolder)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DELETE, item=self.mock_audit_save.PSEUDO_FOLDER + ' - fakepseudofolder', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.get_account')
    def test_render_upload_view_with_prefix_call_audit(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        views.upload(self.request, 'fakecontainer', 'prefixTest')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.UPLOAD, item=self.mock_audit_save.OBJECT + ' - https://fakeurl/fakecontainer/prefixTest', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.requests.get')
    def test_download_call_audit(self, mock_get):
        content = 'ola'
        headers = {'content-type': 'fake/object'}
        mock_get.return_value = fakes.FakeRequestResponse(content=content,
                                                          headers=headers)
        views.download(self.request, 'fakecontainer', 'fakeobject')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DOWNLOAD, item=self.mock_audit_save.OBJECT + ' - fakeobject', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.requests.get')
    def test_metadataview_return_headers_from_container_call_audit(self, mock_get):
        headers = {'content-type': 'fake/container'}
        mock_get.return_value = fakes.FakeRequestResponse(content='',
                                                          headers=headers)
        views.metadataview(self.request, 'fakecontainer')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.LIST, item=self.mock_audit_save.METADATA + ' - fakecontainer', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.requests.get')
    def test_metadataview_return_headers_from_object_call_audit(self, mock_get):
        headers = {'content-type': 'fake/object'}

        mock_get.return_value = fakes.FakeRequestResponse(content='', headers=headers)

        views.metadataview(self.request, 'fakecontainer', 'fakeobject')

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.LIST, item=self.mock_audit_save.METADATA + ' - fakecontainer - fakeobject', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.put_container')
    def test_enable_versioning_call_audit(self, mock_put_container, mock_post_container):

        container = 'fakecontainer'
        views.enable_versioning(self.request, container)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.UPDATE, item=self.mock_audit_save.VERSIONING + ' - fakecontainer', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.delete_container')
    @patch('swiftbrowser.views.client.head_container')
    def test_disable_versioning_call_audit(self, mock_head_container, mock_delete_container, mock_post_container):

        version_location = '_version_fakecontainer'
        mock_head_container.return_value = {'x-versions-location': version_location}

        container = 'fakecontainer'
        views.disable_versioning(self.request, container)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DISABLE, item=self.mock_audit_save.VERSIONING + ' - fakecontainer', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.SWIFTBROWSER, created_at=self.mock_audit_save.NOW)
