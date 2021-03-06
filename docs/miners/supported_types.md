# pyasic
## Supported Miners

Supported miner types are here on this list.  If your miner (or miner version) is not on this list, please feel free to [open an issue on GitHub](https://github.com/UpstreamData/pyasic/issues) to get it added.

## Miner List

##### pyasic currently supports the following miners and subtypes:
* Braiins OS+ Devices:
    * All devices supported by BraiinsOS+ are supported here.
* Stock Firmware Whatsminers:
    * M3X Series:
        * [M30S][pyasic.miners.whatsminer.btminer.M3X.M30S.BTMinerM30S]:
            * [VE10][pyasic.miners.whatsminer.btminer.M3X.M30S.BTMinerM30SVE10]
            * [VG20][pyasic.miners.whatsminer.btminer.M3X.M30S.BTMinerM30SVG20]
            * [VE20][pyasic.miners.whatsminer.btminer.M3X.M30S.BTMinerM30SVE20]
            * [V50][pyasic.miners.whatsminer.btminer.M3X.M30S.BTMinerM30SV50]
        * [M30S+][pyasic.miners.whatsminer.btminer.M3X.M30S_Plus.BTMinerM30SPlus]:
            * [VF20][pyasic.miners.whatsminer.btminer.M3X.M30S_Plus.BTMinerM30SPlusVF20]
            * [VE40][pyasic.miners.whatsminer.btminer.M3X.M30S_Plus.BTMinerM30SPlusVE40]
            * [VG60][pyasic.miners.whatsminer.btminer.M3X.M30S_Plus.BTMinerM30SPlusVG60]
        * [M30S++][pyasic.miners.whatsminer.btminer.M3X.M30S_Plus_Plus.BTMinerM30SPlusPlus]:
            * [VG30][pyasic.miners.whatsminer.btminer.M3X.M30S_Plus_Plus.BTMinerM30SPlusPlusVG30]
            * [VG40][pyasic.miners.whatsminer.btminer.M3X.M30S_Plus_Plus.BTMinerM30SPlusPlusVG40]
        * [M31S][pyasic.miners.whatsminer.btminer.M3X.M31S.BTMinerM31S]
        * [M31S+][pyasic.miners.whatsminer.btminer.M3X.M31S_Plus.BTMinerM31SPlus]:
            * [VE20][pyasic.miners.whatsminer.btminer.M3X.M31S_Plus.BTMinerM31SPlusVE20]
        * [M32S][pyasic.miners.whatsminer.btminer.M3X.M32S.BTMinerM32S]
    * M2X Series:
        * [M20][pyasic.miners.whatsminer.btminer.M2X.M20.BTMinerM20]:
            * [V10][pyasic.miners.whatsminer.btminer.M2X.M20.BTMinerM20V10]
        * [M20S][pyasic.miners.whatsminer.btminer.M2X.M20S.BTMinerM20S]:
            * [V10][pyasic.miners.whatsminer.btminer.M2X.M20S.BTMinerM20SV10]
            * [V20][pyasic.miners.whatsminer.btminer.M2X.M20S.BTMinerM20SV20]
        * [M20S+][pyasic.miners.whatsminer.btminer.M2X.M20S_Plus.BTMinerM20SPlus]
        * [M21][pyasic.miners.whatsminer.btminer.M2X.M21.BTMinerM21]
        * [M21S][pyasic.miners.whatsminer.btminer.M2X.M21S.BTMinerM21S]:
            * [V20][pyasic.miners.whatsminer.btminer.M2X.M21S.BTMinerM21SV20]
            * [V60][pyasic.miners.whatsminer.btminer.M2X.M21S.BTMinerM21SV60]
        * [M21S+][pyasic.miners.whatsminer.btminer.M2X.M21S_Plus.BTMinerM21SPlus]
* Stock Firmware Antminers:
    * X19 Series:
        * [S19][pyasic.miners.antminer.bmminer.X19.S19.BMMinerS19]
        * [S19 Pro][pyasic.miners.antminer.bmminer.X19.S19_Pro.BMMinerS19Pro]
        * [S19a][pyasic.miners.antminer.bmminer.X19.S19a.BMMinerS19a]
        * [S19j][pyasic.miners.antminer.bmminer.X19.S19j.BMMinerS19j]
        * [S19j Pro][pyasic.miners.antminer.bmminer.X19.S19j_Pro.BMMinerS19jPro]
        * [T19][pyasic.miners.antminer.bmminer.X19.T19.BMMinerT19]
    * X17 Series:
        * [S17][pyasic.miners.antminer.bmminer.X17.S17.BMMinerS17]
        * [S17+][pyasic.miners.antminer.bmminer.X17.S17_Plus.BMMinerS17Plus]
        * [S17 Pro][pyasic.miners.antminer.bmminer.X17.S17_Pro.BMMinerS17Pro]
        * [S17e][pyasic.miners.antminer.bmminer.X17.S17e.BMMinerS17e]
        * [T17][pyasic.miners.antminer.bmminer.X17.T17.BMMinerT17]
        * [T17+][pyasic.miners.antminer.bmminer.X17.T17_Plus.BMMinerT17Plus]
        * [T17e][pyasic.miners.antminer.bmminer.X17.T17e.BMMinerT17e]
    * X9 Series:
        * [S9][pyasic.miners.antminer.bmminer.X9.S9.BMMinerS9]
        * [S9i][pyasic.miners.antminer.bmminer.X9.S9i.BMMinerS9i]
        * [T9][pyasic.miners.antminer.bmminer.X9.T9.BMMinerT9]
* Stock Firmware Avalonminers:
    * A7X Series:
        * [A721][pyasic.miners.avalonminer.cgminer.A7X.A721.CGMinerAvalon721]
        * [A741][pyasic.miners.avalonminer.cgminer.A7X.A741.CGMinerAvalon741]
        * [A761][pyasic.miners.avalonminer.cgminer.A7X.A761.CGMinerAvalon761]
    * A8X Series:
        * [A821][pyasic.miners.avalonminer.cgminer.A8X.A821.CGMinerAvalon821]
        * [A841][pyasic.miners.avalonminer.cgminer.A8X.A841.CGMinerAvalon841]
        * [A851][pyasic.miners.avalonminer.cgminer.A8X.A851.CGMinerAvalon851]
    * A9X Series:
        * [A921][pyasic.miners.avalonminer.cgminer.A9X.A921.CGMinerAvalon921]
    * A10X Series:
        * [A1026][pyasic.miners.avalonminer.cgminer.A10X.A1026.CGMinerAvalon1026]
        * [A1047][pyasic.miners.avalonminer.cgminer.A10X.A1047.CGMinerAvalon1047]
        * [A1066][pyasic.miners.avalonminer.cgminer.A10X.A1066.CGMinerAvalon1066]
