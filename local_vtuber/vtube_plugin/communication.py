import asyncio
import json
import websockets


class CommunicationManager:
    def __init__(self, uri, plugin_name="Assistant", plugin_developer='AlekGreen'):
        self.uri = uri
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.auth_token = None
        self.websocket = None
        self.reconnect_delay = 1

    def set_auth_token(self, auth_token):
        self.auth_token = auth_token

    def get_msg_template(self):
        return {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": f"AssistantID",
        }

    async def authenticate_session(self):
        msg = self.get_msg_template()
        msg["messageType"] = "AuthenticationRequest"
        msg["data"] = {
            "pluginName": self.plugin_name,
            "pluginDeveloper": self.plugin_developer,
            "authenticationToken": self.auth_token
        }
        res = await self.send(msg)
        print(res)

    async def connect(self):
        try:
            if not self.websocket or self.websocket.closed:
                self.websocket = await websockets.connect(self.uri, ping_interval=3)
                await self.authenticate_session()
                self.reconnect_delay = 1
                asyncio.create_task(self.ping_pong_handler())
        except websockets.ConnectionClosed:
            await self.handle_reconnect()
        except Exception as e:
            print(f"Failed to connect: {e}")
            await self.handle_reconnect()

    async def ping_pong_handler(self):
        while self.websocket and not self.websocket.closed:
            try:
                pong_waiter = await self.websocket.ping()
                await asyncio.wait_for(pong_waiter, timeout=10)
            except asyncio.TimeoutError:
                print("Ping timeout. Connection might be lost. Reconnecting...")
                await self.handle_reconnect()
            except websockets.ConnectionClosed:
                await self.handle_reconnect()
            await asyncio.sleep(10)

    async def ensure_open(self):
        if self.websocket is None or self.websocket.closed:
            await self.connect()

    async def send(self, msg):
        await self.ensure_open()
        await self.websocket.send(json.dumps(msg))
        return await self.websocket.recv()

    async def handle_reconnect(self):
        await self.close()
        print(f"Reconnecting in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, 60)
        await self.connect()

    async def close(self):
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None
