from miners.bmminer import BMMiner


class HiveonT9(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "T9"
        self.api_type = "Hiveon"

    def __repr__(self) -> str:
        return f"HiveonT9: {str(self.ip)}"


    async def get_bad_boards(self) -> list:
        """Checks for and provides list of non working boards."""
        board_stats = await self.api.stats()
        stats = board_stats['STATS'][1]
        bad_boards = []
        board_chains = {6: [2, 9, 10], 7: [3, 11, 12], 8: [4, 13, 14]}
        for board in board_chains:
            for chain in board_chains[board]:
                count = stats[f"chain_acn{chain}"]
                chips = stats[f"chain_acs{chain}"].replace(" ", "")
                if not count == 18 or "x" in chips:
                    bad_boards.append({"board": board, "chain": chain, "chip_count": count, "chip_status": chips})
        return bad_boards
