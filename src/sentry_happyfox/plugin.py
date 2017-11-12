from __future__ import absolute_import
import base64
import json
import requests
from urlparse import urljoin

from sentry.plugins.bases.issue2 import IssuePlugin2
from sentry.utils.http import absolute_uri


def make_choices(options):
    return [(option['id'], option['name']) for option in options]


class HappyFoxPlugin(IssuePlugin2):
    descripition = 'Integrate with HappyFox by converting Sentry issues to tickets'
    slug = 'happyfox'
    title = 'HappyFox'
    conf_title = title
    conf_key = 'happyfox'
    author = 'HappyFox Team'
    author_url = 'https://github.com/happyfoxinc/sentry-happyfox'
    version = '1.0.0'
    resource_links = (
        ('Bug Tracker', 'https://github.com/happyfoxinc/sentry-happyfox/issues'),
    )

    def get_configure_plugin_fields(self, request, project, **kwargs):
        account_url = self.get_option('account_url', project)
        api_key = self.get_option('api_key', project)
        auth_code = self.get_option('auth_code', project)
        categories = []
        default_category = self.get_option('category', project)
        default_staff = self.get_option('staff', project)
        staff = []
        if all([account_url, api_key, auth_code]):
            categories = self._get_account_categories(project)
            staff = self._get_account_staff(project)

        return [
            {
                "name": "account_url",
                "label": "HappyFox Account URL",
                "default": "",
                "type": "text",
                "placeholder": "https://yourcompany.happyfox.com",
                "help": "Enter the domain name for your HappyFox Account"
            },
            {
                "name": "api_key",
                "label": "API Key",
                "default": "",
                "type": "text",
                "placeholder": "",
            },
            {
                "name": "auth_code",
                "label": "Auth Code",
                "default": "",
                "type": "secret",
                "placeholder": "",
            },
            {
                "name": "contact_name",
                "label": "Contact Name",
                "default": "Sentry",
                "type": "text",
                "placeholder": "Sentry",
                "help": "Enter the name of the contact from which the tickets have to be created with in HappyFox"
            },
            {
                "name": "contact_email",
                "label": "Contact Email",
                "type": "email",
                "placeholder": "sentry@sentry.com",
                "help": "Enter the email of the contact from which the tickets have to be created with in HappyFox"
            },
            {
                "name": "private_note_staff",
                "label": "HappyFox Staff",
                "type": "select",
                "default": default_staff,
                "choices": staff,
                "help": "Select the staff by whom the private notes are to be posted while linking tickets to sentry issue",
                "required": False
            },
            {
                "name": "subject_prefix",
                "label": "Subject Prefix",
                "type": "text",
                "default": "[Sentry]",
                "help": "The default prefix to be added to the new tickets created from sentry",
                "required": False
            },
            {
                "name": "category",
                "label": "Category",
                "default": default_category,
                "type": "select",
                "choices": categories,
                "help": "Select the category in which the tickets are to be created",
                "required": False
            }
        ]

    def is_configured(self, request, project, **kwargs):
        return all(self.get_option(k, project) for k in ('account_url', 'api_key',
                                                         'auth_code', 'category'))

    def _construct_url(self, url, project):
        base_url = urljoin(self.get_option('account_url', project), 'api/1.1/json/')
        url = urljoin(base_url, url)
        return url

    def get_issue_url(self, group, issue_id, **kwargs):
        url = self._construct_url("/staff/ticket/", group.project)
        return "{0}{1}".format(url, issue_id)

    def _get_authentication_token(self, project):
        api_key = self.get_option('api_key', project)
        auth_code = self.get_option('auth_code', project)
        token = "Basic {0}".format(base64.b64encode('{0}:{1}'.format(api_key, auth_code)))
        return token

    def _make_get_request(self, url, project):
        url = self._construct_url(url, project)
        token = self._get_authentication_token(project)
        headers = {
            "Authorization": token
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []

    def _make_post_request(self, url, data, project):
        url = self._construct_url(url, project)
        token = self._get_authentication_token(project)
        headers = {
            "Content-Type": "application/json",
            "Authorization": token
        }
        response = requests.post(url, data, headers=headers)
        return response.json()

    def _get_account_categories(self, project):
        url = "categories/"
        categories = self._make_get_request(url, project)
        return make_choices(categories)

    def _get_account_staff(self, project):
        url = 'staff/'
        staff = self._make_get_request(url, project)
        return make_choices(staff)

    def get_new_issue_fields(self, request, group, event, **kwargs):
        fields = super(HappyFoxPlugin, self).get_new_issue_fields(request, group, event, **kwargs)
        return fields

    def get_link_existing_issue_fields(self, request, group, event, **kwargs):
        return [
            {
                'name': 'issue_id',
                'label': 'Ticket ID',
                'default': '',
                'placeholder': 'e.g. 123',
                'type': 'number'
            },
            {
                "name": "text",
                "label": "Message",
                "default": "Related Sentry Issue: {}".format(absolute_uri(group.get_absolute_url())),
                "type": "textarea",
                "help": "Enter the text that is to be posted as update in HappyFox"
            }
        ]

    def link_issue(self, request, group, form_data, **kwargs):
        project = group.project
        json_data = json.dumps({
            'staff': self.get_option('private_note_staff', project),
            'text': form_data.get('text')
        })
        print json_data
        issue_id = form_data.get('issue_id')
        url = 'ticket/{}/staff_pvtnote/'.format(issue_id)
        response = self._make_post_request(url, json_data, project)
        return {
            'title': response.get('subject')
        }

    def create_issue(self, request, group, form_data, **kwargs):
        project = group.project
        json_data = json.dumps({
            "category": self.get_option('category', project),
            "subject": "{0} {1}".format(
                str(self.get_option('subject_prefix', project)), form_data.get('title')),
            "text": form_data.get('description'),
            "email": self.get_option('contact_email', project),
            "name": self.get_option('contact_name', project),
            "title": form_data.get('subject')
        })
        response = self._make_post_request("tickets/", json_data, project)
        return response['id']
