from .auth import AuthManager
from .communication import CommunicationManager
from .parameters import ParameterManager
from .audio_utils import AudioProcessor
from .constants import DEFAULT_EXPRESSIONS


class VTubeConnector:
    def __init__(self, plugin_name="Assistant", plugin_developer='AlekGreen', port=8001, plugin_icon=None):
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.port = port
        self.plugin_icon = plugin_icon
        self.uri = f"ws://localhost:{port}"
        self.communicator = CommunicationManager(self.uri, self.plugin_name, self.plugin_developer)
        self.auth_manager = AuthManager(self.plugin_name, self.plugin_developer, self.communicator)
        self.parameter_manager = ParameterManager(self.communicator)
        self.audio_processor = AudioProcessor(self.communicator)
        print(self.audio_processor)

    async def start(self):
        await self.auth_manager.init_connection()
        await self.communicator.connect()
        await self.parameter_manager.setup_custom_parameters()

    async def reauthenticate(self):
        await self.communicator.connect()

    async def get_hotkeys(self):
        msg = self.communicator.get_msg_template()
        msg["messageType"] = "HotkeysInCurrentModelRequest"
        result = await self.communicator.send(msg)
        return result

    async def execute_hotkey(self, hotkey):
        msg = self.communicator.get_msg_template()
        msg["messageType"] = "HotkeyTriggerRequest"
        msg["data"] = {
            "hotkeyID": DEFAULT_EXPRESSIONS[hotkey]
        }
        result = await self.communicator.send(msg)
        return result
