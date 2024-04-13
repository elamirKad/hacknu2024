import asyncio

from local_vtuber.vtube_plugin.connector import VTubeConnector

if __name__ == "__main__":
    connector = VTubeConnector()
    asyncio.run(connector.start())
    AsyncSpeechSynthesizer(self.connector)
