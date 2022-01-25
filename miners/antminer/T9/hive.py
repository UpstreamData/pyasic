from miners.bmminer import BMMiner


class HiveonT9(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "T9"
        self.api_type = "Hiveon"

    def __repr__(self) -> str:
        return f"HiveonT9: {str(self.ip)}"

    async def get_board_info(self) -> dict:
        """Gets data on each board and chain in the miner."""
        board_stats = await self.api.stats()
        stats = board_stats['STATS'][1]
        boards = {}
        board_chains = {6: [2, 9, 10], 7: [3, 11, 12], 8: [4, 13, 14]}
        for idx, board in enumerate(board_chains):
            boards[board] = []
            for chain in board_chains[board]:
                count = stats[f"chain_acn{chain}"]
                chips = stats[f"chain_acs{chain}"].replace(" ", "")
                if not count == 18 or "x" in chips:
                    nominal = False
                else:
                    nominal = True
                boards[board].append({
                    "chain": chain,
                    "chip_count": count,
                    "chip_status": chips,
                    "nominal": nominal
                })
        return boards

    async def get_bad_boards(self) -> dict:
        """Checks for and provides list of non working boards."""
        boards = await self.get_board_info()
        bad_boards = {}
        for board in boards.keys():
            for chain in boards[board]:
                if not chain["chip_count"] == 18 or "x" in chain["chip_status"]:
                    if board not in bad_boards.keys():
                        bad_boards[board] = []
                    bad_boards[board].append(chain)
        return bad_boards