import json

class ParameterManager:
    def __init__(self, communicator):
        self.parameters = [
            {
                "name": "CustomSoundTracker",
                "explanation": "Tracks custom sound.",
                "min": 0,
                "max": 100,
                "default": 0
            },
            {
                "name": "BrowHeightLeft",
                "explanation": "Controls the height of the left brow.",
                "min": 0,
                "max": 100,
                "default": 80
            },
            {
                "name": "BrowHeightRight",
                "explanation": "Controls the height of the right brow.",
                "min": 0,
                "max": 100,
                "default": 80
            },
            {
                "name": "FaceLeftRightRotation",
                "explanation": "Controls the left/right rotation of the face.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "FaceUpDownRotation",
                "explanation": "Controls the up/down rotation of the face.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "FaceLeanRotation",
                "explanation": "Controls the leaning rotation of the face.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "EyeOpenRightCustom",
                "explanation": "Controls how much the right eye is open.",
                "min": 0,
                "max": 100,
                "default": 80
            },
            {
                "name": "EyeOpenLeftCustom",
                "explanation": "Controls how much the left eye is open.",
                "min": 0,
                "max": 100,
                "default": 80
            },
            {
                "name": "EyeX",
                "explanation": "Controls the X-axis movement of the eyes.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "EyeY",
                "explanation": "Controls the Y-axis movement of the eyes.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "MouthSmileCustom",
                "explanation": "Controls the degree of smiling.",
                "min": 0,
                "max": 100,
                "default": 80
            },
            {
                "name": "BodyRotationX",
                "explanation": "Controls the X-axis rotation of the body.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "BodyRotationZ",
                "explanation": "Controls the Z-axis rotation of the body.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "BodyRotationY",
                "explanation": "Controls the Y-axis rotation of the body.",
                "min": -100,
                "max": 100,
                "default": 0
            },
            {
                "name": "TongueOutCustom",
                "explanation": "Controls the degree to which the tongue is out.",
                "min": 0,
                "max": 100,
                "default": 50
            }
        ]
        self.communicator = communicator
        self.parameter_values = {param['name']: param['default'] for param in self.parameters}

    async def get_tracking_parameters(self):
        msg = self.communicator.get_msg_template()
        msg["messageType"] = "InputParameterListRequest"
        response = await self.communicator.send(msg)
        return response

    def find_custom_parameter(self, parameters_json, parameter_name):
        try:
            data = json.loads(parameters_json)
            custom_params = data.get('data', {}).get('customParameters', [])
            for param in custom_params:
                if param['name'] == parameter_name:
                    return param
            return None
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return None

    async def create_custom_parameter(self, parameter):
        name, explanation, min_value, max_value, default_value = (
            parameter['name'], parameter['explanation'],
            parameter['min'], parameter['max'], parameter['default']
        )

        if not (4 <= len(name) <= 32 and name.isalnum()):
            raise ValueError("Parameter name must be unique, alphanumeric, and between 4 and 32 characters in length.")

        if len(explanation) >= 256:
            raise ValueError("Explanation must be shorter than 256 characters.")

        if not (-1000000 <= min_value <= 1000000 and -1000000 <= max_value <= 1000000 and -1000000 <= default_value <= 1000000):
            raise ValueError("Min, Max and Default values have to be between -1000000 and 1000000.")

        msg = self.communicator.get_msg_template()
        msg["messageType"] = "ParameterCreationRequest"
        msg["data"] = {
            "parameterName": name,
            "explanation": explanation,
            "min": min_value,
            "max": max_value,
            "defaultValue": default_value
        }
        response = await self.communicator.send(msg)
        return response

    async def setup_custom_parameters(self):
        tracking_params_json = await self.get_tracking_parameters()
        for parameter in self.parameters:
            custom_param = self.find_custom_parameter(tracking_params_json, parameter['name'])
            if custom_param is None:
                await self.create_custom_parameter(parameter)

    async def get_parameter_value(self, parameter_name):
        msg = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeUniqueID",
            "messageType": "ParameterValueRequest",
            "data": {
                "name": parameter_name
            }
        }

        response = await self.communicator.send(msg)
        return json.loads(response)

    async def get_current_parameter_values(self):
        current_params = []

        for param in self.parameters:
            response_data = await self.get_parameter_value(param['name'])
            print(response_data)
            if response_data.get("data"):
                current_params.append(response_data["data"])
            else:
                print(f"Parameter {param['name']} not found or no response.")

        return current_params

    def set_parameter_value(self, name, value):
        if name in self.parameter_values:
            if self.parameter_values[name] != value:
                self.parameter_values[name] = value
        else:
            print(f"Parameter '{name}' not found.")

    async def send_parameter_values(self):
        parameter_data = [
            {"id": name, "value": self.parameter_values[name]}
            for name in self.parameter_values
        ]
        msg = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeUniqueID",
            "messageType": "InjectParameterDataRequest",
            "data": {
                "faceFound": False,
                "mode": "set",
                "parameterValues": parameter_data
            }
        }
        response = await self.communicator.send(msg)
        return response
