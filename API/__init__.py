import asyncio
import json
import ipaddress
import warnings
import logging


class APIError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return "Incorrect API parameters."


class APIWarning(Warning):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return "Incorrect API parameters."


class BaseMinerAPI:
    def __init__(self, ip: str, port: int = 4028) -> None:
        # api port, should be 4028
        self.port = port
        # ip address of the miner
        self.ip = ipaddress.ip_address(ip)

    def get_commands(self) -> list:
        """Get a list of command accessible to a specific type of API on the miner."""
        return [
            func
            for func in
            # each function in self
            dir(self)
            if callable(getattr(self, func)) and
            # no __ methods
            not func.startswith("__") and
            # remove all functions that are in this base class
            func
            not in [
                func
                for func in dir(BaseMinerAPI)
                if callable(getattr(BaseMinerAPI, func))
            ]
        ]

    async def multicommand(self, *commands: str) -> dict:
        """Creates and sends multiple commands as one command to the miner."""
        logging.debug(f"{self.ip}: Sending multicommand: {[*commands]}")
        # split the commands into a proper list
        user_commands = [*commands]
        allowed_commands = self.get_commands()
        # make sure we can actually run the command, otherwise it will fail
        commands = [command for command in user_commands if command in allowed_commands]
        for item in list(set(user_commands) - set(commands)):
            warnings.warn(
                f"""Removing incorrect command: {item}
If you are sure you want to use this command please use API.send_command("{item}", ignore_errors=True) instead.""",
                APIWarning,
            )
        # standard multicommand format is "command1+command2"
        # doesnt work for S19 which is dealt with in the send command function
        command = "+".join(commands)
        data = None
        try:
            data = await self.send_command(command)
        except APIError as e:
            try:
                data = {}
                # S19 handler, try again
                for cmd in command.split("+"):
                    data[cmd] = []
                    data[cmd].append(await self.send_command(cmd))
            except APIError as e:
                raise APIError(e)
            except Exception as e:
                logging.warning(f"{self.ip}: API Multicommand Error: {e}")
        if data:
            logging.debug(f"{self.ip}: Received multicommand data.")
            return data

    async def send_command(
        self,
        command: str,
        parameters: str or int or bool = None,
        ignore_errors: bool = False,
    ) -> dict:
        """Send an API command to the miner and return the result."""
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(self.ip), self.port)
        # handle OSError 121
        except OSError as e:
            if e.winerror == "121":
                logging.warning("Semaphore Timeout has Expired.")
            return {}

        # create the command
        cmd = {"command": command}
        if parameters is not None:
            cmd["parameter"] = parameters

        # send the command
        writer.write(json.dumps(cmd).encode("utf-8"))
        await writer.drain()

        # instantiate data
        data = b""

        # loop to receive all the data
        try:
            while True:
                d = await reader.read(4096)
                if not d:
                    break
                data += d
        except Exception as e:
            logging.warning(f"{self.ip}: API Command Error: {e}")

        data = self.load_api_data(data)

        # close the connection
        writer.close()
        await writer.wait_closed()

        # check for if the user wants to allow errors to return
        if not ignore_errors:
            # validate the command succeeded
            validation = self.validate_command_output(data)
            if not validation[0]:
                logging.warning(f"{self.ip}: API Command Error: {validation[1]}")
                raise APIError(validation[1])

        return data

    @staticmethod
    def validate_command_output(data: dict) -> tuple:
        """Check if the returned command output is correctly formatted."""
        # check if the data returned is correct or an error
        # if status isn't a key, it is a multicommand
        if "STATUS" not in data.keys():
            for key in data.keys():
                # make sure not to try to turn id into a dict
                if not key == "id":
                    # make sure they succeeded
                    if "STATUS" in data[key][0].keys():
                        if data[key][0]["STATUS"][0]["STATUS"] not in ["S", "I"]:
                            # this is an error
                            return False, f"{key}: " + data[key][0]["STATUS"][0]["Msg"]
        elif "id" not in data.keys():
            if data["STATUS"] not in ["S", "I"]:
                return False, data["Msg"]
        else:
            # make sure the command succeeded
            if data["STATUS"][0]["STATUS"] not in ("S", "I"):
                # this is an error
                if data["STATUS"][0]["STATUS"] not in ("S", "I"):
                    return False, data["STATUS"][0]["Msg"]
        return True, None

    @staticmethod
    def load_api_data(data: bytes) -> dict:
        """Convert API data from JSON to dict"""
        str_data = None
        try:
            # some json from the API returns with a null byte (\x00) on the end
            if data.endswith(b"\x00"):
                # handle the null byte
                str_data = data.decode("utf-8")[:-1]
            else:
                # no null byte
                str_data = data.decode("utf-8")
            # fix an error with a btminer return having an extra comma that breaks json.loads()
            str_data = str_data.replace(",}", "}")
            # fix an error with a btminer return having a newline that breaks json.loads()
            str_data = str_data.replace("\n", "")
            # fix an error with a bmminer return not having a specific comma that breaks json.loads()
            str_data = str_data.replace("}{", "},{")
            # fix an error with a bmminer return  having a specific comma that breaks json.loads()
            str_data = str_data.replace("[,{", "[{")
            # fix an error with a btminer return  having a specific comma that breaks json.loads()
            str_data = str_data.replace("inf", "0")
            # parse the json
            parsed_data = json.loads(str_data)
        # handle bad json
        except json.decoder.JSONDecodeError as e:
            raise APIError(f"Decode Error {e}: {str_data}")
        return parsed_data
