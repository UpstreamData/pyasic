from miners.bmminer import BMMiner


class HiveonT9(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "T9"
        self.api_type = "Hiveon"

    def __repr__(self) -> str:
        return f"HiveonT9: {str(self.ip)}"

    async def get_board_info(self) -> list:
        """Gets data on each board and chain in the miner."""
        board_stats = await self.api.stats()
        stats = board_stats['STATS'][1]
        boards = []
        board_chains = {6: [2, 9, 10], 7: [3, 11, 12], 8: [4, 13, 14]}
        for idx, board in enumerate(board_chains):
            boards.append({"board": board, "chains": []})
            for chain in board_chains[board]:
                count = stats[f"chain_acn{chain}"]
                chips = stats[f"chain_acs{chain}"].replace(" ", "")
                boards[idx]["chains"].append({
                    "chain": chain,
                    "chip_count": count,
                    "chip_status": chips
                })
        return boards

    async def get_bad_boards(self) -> list:
        """Checks for and provides list of non working boards."""
        boards = await self.get_board_info()
        bad_boards = []
        idx = 0
        for board in boards:
            bad_boards.append({"board": board["board"], "chains": []})
            for chain in board["chains"]:
                if not chain["chip_count"] == 18 or "x" in chain["chip_status"]:
                    bad_boards[idx]["chains"].append(chain)
            if not bad_boards[idx]["chains"]:
                del bad_boards[idx]
                idx -= 1
            idx += 1
        return bad_boards
