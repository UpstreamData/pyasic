from API import BaseMinerAPI


class CGMinerAPI(BaseMinerAPI):
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

