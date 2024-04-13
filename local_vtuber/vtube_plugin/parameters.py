import json


class ParameterManager:
    def __init__(self, communicator):
        self.custom_param_name = "CustomSoundTracker"
        self.custom_param_explanation = "Tracks custom sound."
        self.custom_param_min = 0
        self.custom_param_max = 100
        self.custom_param_default = 0
        self.communicator = communicator

    async def get_tracking_parameters(self):
        msg = self.communicator.get_msg_template()
        msg["messageType"] = "InputParameterListRequest"
        response = await self.communicator.send(msg)
        return response

    def find_custom_parameter(self, parameters_json, custom_param_name):
        try:
            data = json.loads(parameters_json)
            custom_params = data.get('data', {}).get('customParameters', [])
            for param in custom_params:
                if param['name'] == custom_param_name:
                    return param
            return None
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return None

    async def create_custom_parameter(self, parameter_name, explanation, min_value, max_value, default_value):
        if not (4 <= len(parameter_name) <= 32 and parameter_name.isalnum()):
            raise ValueError("Parameter name must be unique, alphanumeric, and between 4 and 32 characters in length.")

        if len(explanation) >= 256:
            raise ValueError("Explanation must be shorter than 256 characters.")

        if not (
                -1000000 <= min_value <= 1000000 and -1000000 <= max_value <= 1000000 and -1000000 <= default_value <= 1000000):
            raise ValueError("Min, Max and Default values have to be between -1000000 and 1000000.")

        msg = self.communicator.get_msg_template()
        msg["messageType"] = "ParameterCreationRequest"
        msg["data"] = {
            "parameterName": parameter_name,
            "explanation": explanation,
            "min": min_value,
            "max": max_value,
            "defaultValue": default_value
        }
        response = await self.communicator.send(msg)
        return response

    async def setup_custom_parameter(self):
        tracking_params_json = await self.get_tracking_parameters()
        custom_param = self.find_custom_parameter(tracking_params_json, self.custom_param_name)
        if custom_param is None:
            await self.create_custom_parameter(
                self.custom_param_name,
                self.custom_param_explanation,
                self.custom_param_min,
                self.custom_param_max,
                self.custom_param_default
            )
