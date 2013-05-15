"""RequestHandlers for Web service"""

__author__ = 'mparramon'

import utils
from auth import get_auth_service

import json
import logging
import random
import string


from oauth2client.client import AccessTokenRefreshError


class IndexHandler(utils.BaseHandler):
    """Renders the main page that is mainly used for authentication only so far"""

    def get(self, test):

        if test is None:
            scopes = ' '.join(utils.COMMON_SCOPES + utils.REAL_SCOPES)
        else:
            scopes = ' '.join(utils.COMMON_SCOPES + utils.TEST_SCOPES)

        request_visible_actions = ' '.join(utils.REQUEST_VISIBLE_ACTIONS)
        reconnect = (self.request.get("reconnect") == "true")
        template = utils.JINJA.get_template("service/templates/icebreaker.html")
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        self.session["state"] = state
        self.response.out.write(template.render({"client_id": utils.CLIENT_ID, "state": state, "scopes": scopes, "actions": request_visible_actions, "reconnect": reconnect}))


class ListHandler(utils.BaseHandler):

    def get(self, test):
        """Retrieve timeline cards for the current user."""

        self.response.content_type = "application/json"

        gplus_id = self.session.get("gplus_id")
        service = get_auth_service(gplus_id, test)

        if service is None:
            self.response.status = 401
            self.response.out.write(utils.createError(401, "Current user not connected."))
            return
        try:
            # Retrieve timeline cards and return as reponse
            result = service.timeline().list().execute()
            self.response.status = 200
            self.response.out.write(json.dumps(result))
        except AccessTokenRefreshError:
            self.response.status = 500
            self.response.out.write(utils.createError(500, "Failed to refresh access token."))


class NewCardHandler(utils.BaseHandler):

    def post(self, test):
        """Create a new timeline card for the current user."""

        self.response.content_type = "application/json"

        gplus_id = self.session.get("gplus_id")
        service = get_auth_service(gplus_id, test)

        if service is None:
            self.response.status = 401
            self.response.out.write(utils.createError(401, "Current user not connected."))
            return

        message = self.request.body

        data = json.loads(message)

        body = {}
        body["text"] = 'xing-icebreaker says: ' + data["text"]

        try:
            # Insert timeline card and return as reponse
            result = service.timeline().insert(body=body).execute()
            self.response.status = 200
            self.response.out.write(json.dumps(result))
        except AccessTokenRefreshError:
            self.response.status = 500
            self.response.out.write(utils.createError(500, "Failed to refresh access token."))

class InitCardHandler(utils.BaseHandler):

    def post(self, test):
        """Send the first Xing Icebreaker card."""

        self.response.content_type = "application/json"

        gplus_id = self.session.get("gplus_id")
        service = get_auth_service(gplus_id, test)

        if service is None:
            self.response.status = 401
            self.response.out.write(utils.createError(401, "Current user not connected."))
            return

        json_data = open("service/templates/icebreaker/bundle.json")
        body = json.load(json_data)
        print body

        try:
            # Insert timeline card and return as reponse
            result = service.timeline().insert(body=body).execute()
            self.response.status = 200
            self.response.out.write(json.dumps(result))
        except AccessTokenRefreshError:
            self.response.status = 500
            self.response.out.write(utils.createError(500, "Failed to refresh access token."))

class ContactInfoCardHandler(utils.BaseHandler):

    def post(self, test):
        """Send the card with info about one contact."""
        print 'contact infooooooooooooooooooooooooooooooooooooooooo'

        self.response.content_type = "application/json"

        gplus_id = self.session.get("gplus_id")
        service = get_auth_service(gplus_id, test)

        if service is None:
            self.response.status = 401
            self.response.out.write(utils.createError(401, "Current user not connected."))
            return

        json_data = open("service/templates/icebreaker/contact_info.json")
        body = json.load(json_data)
        print body

        try:
            # Insert timeline card and return as reponse
            result = service.timeline().insert(body=body).execute()
            self.response.status = 200
            self.response.out.write(json.dumps(result))
        except AccessTokenRefreshError:
            self.response.status = 500
            self.response.out.write(utils.createError(500, "Failed to refresh access token."))

class AttachmentHandler(utils.BaseHandler):
    """Retrieves an attachment using the current user's credentials"""

    def get(self, test, timelineId, attachmentId):
        gplus_id = self.session.get("gplus_id")
        service = get_auth_service(gplus_id, test)
        if service is None:
            self.response.content_type = "application/json"
            self.response.status = 401
            self.response.out.write(utils.createError(401, "Invalid credentials."))
            return

        attachment_metadata = service.timeline().attachments().get(
            itemId=timelineId, attachmentId=attachmentId).execute()
        content_type = str(attachment_metadata.get("contentType"))
        content_url = attachment_metadata.get("contentUrl")
        resp, content = service._http.request(content_url)

        if resp.status == 200:
            self.response.content_type = content_type
            self.response.out.write(content)
        else:
            logging.info(resp)
            self.response.content_type = "application/json"
            self.response.status = resp.status
            self.response.out.write(utils.createError(resp.status, "Unable to retrieve attachment."))


ICEBREAKER_ROUTES = [
    (r"(/icebreaker)?/attachment/(.*)/(.*)", AttachmentHandler),
    (r"(/icebreaker)?/", IndexHandler),
    (r"(/icebreaker)?/list", ListHandler),
    (r"(/icebreaker)?/new", NewCardHandler),
    (r"(/icebreaker)?/init", InitCardHandler),
    (r"(/icebreaker)?/contact_info", ContactInfoCardHandler)
]
