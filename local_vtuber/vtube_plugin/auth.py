import os
import json
from .constants import AUTH_TOKEN_FILE


class AuthManager:
    def __init__(self, plugin_name, plugin_developer, communicator):
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.auth_token = None
        self.AUTH_TOKEN_FILE = AUTH_TOKEN_FILE
        self.communicator = communicator

    def save_auth_token(self):
        """Saves the auth token to a file."""
        with open(self.AUTH_TOKEN_FILE, 'w') as f:
            f.write(self.auth_token)

    def load_auth_token(self):
        """Loads the auth token from a file, if it exists."""
        if os.path.exists(self.AUTH_TOKEN_FILE):
            with open(self.AUTH_TOKEN_FILE, 'r') as f:
                self.auth_token = f.read().strip()
                return self.auth_token
        return None

    async def authenticate_session(self):
        if self.auth_token is None:
            if self.load_auth_token() is None:
                await self.init_connection()

        msg = self.communicator.get_msg_template()
        msg["messageType"] = "AuthenticationRequest"
        msg["data"] = {
            "pluginName": self.plugin_name,
            "pluginDeveloper": self.plugin_developer,
            "authenticationToken": self.auth_token
        }
        await self.communicator.send(msg)

    async def init_connection(self):
        self.load_auth_token()
        if self.auth_token is None:
            auth_msg = self.communicator.get_msg_template()
            auth_msg["messageType"] = "AuthenticationTokenRequest"
            auth_msg["data"] = {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer
            }
            auth_response = await self.communicator.send(auth_msg)

            auth_response = json.loads(auth_response)
            self.auth_token = auth_response["data"]["authenticationToken"]
            self.save_auth_token()
        self.communicator.set_auth_token(self.auth_token)
        await self.communicator.authenticate_session()

        await self.authenticate_session()

