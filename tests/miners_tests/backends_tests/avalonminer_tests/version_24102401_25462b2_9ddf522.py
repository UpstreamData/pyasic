"""Tests for hammer miners with firmware dating 2023-05-28 17-20-35 CST"""

import unittest
from dataclasses import fields
from unittest.mock import patch

from pyasic import APIError, MinerData
from pyasic.data import Fan, HashBoard
from pyasic.device.algorithm import SHA256Unit
from pyasic.miners.avalonminer import CGMinerAvalon1566

POOLS = [
    {
        "url": "stratum+tcp://stratum.pool.io:3333",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3334",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3335",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
]


data = {
    CGMinerAvalon1566: {
        "rpc_version": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 986,
                    "Code": 22,
                    "Msg": "CGMiner versions",
                    "Description": "cgminer 4.11.1",
                }
            ],
            "VERSION": [
                {
                    "CGMiner": "4.11.1",
                    "API": "3.7",
                    "STM8": "20.08.01",
                    "PROD": "AvalonMiner 15-194",
                    "MODEL": "15-194",
                    "HWTYPE": "MM4v2_X3",
                    "SWTYPE": "MM319",
                    "VERSION": "24102401_25462b2_9ddf522",
                    "LOADER": "d0d779de.00",
                    "DNA": "020100008c699117",
                    "MAC": "123456789012",
                    "UPAPI": "2",
                }
            ],
            "id": 1,
        },
        "rpc_devs": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 986,
                    "Code": 9,
                    "Msg": "1 ASC(s)",
                    "Description": "cgminer 4.11.1",
                }
            ],
            "DEVS": [
                {
                    "ASC": 0,
                    "Name": "AVA10",
                    "ID": 0,
                    "Enabled": "Y",
                    "Status": "Alive",
                    "Temperature": -273.0,
                    "MHS av": 192796247.36,
                    "MHS 30s": 197497926.49,
                    "MHS 1m": 197266944.16,
                    "MHS 5m": 186968586.55,
                    "MHS 15m": 124648835.18,
                    "Accepted": 148,
                    "Rejected": 1,
                    "Hardware Errors": 0,
                    "Utility": 9.61,
                    "Last Share Pool": 0,
                    "Last Share Time": 975,
                    "Total MH": 178226436366.0,
                    "Diff1 Work": 41775104,
                    "Difficulty Accepted": 38797312.0,
                    "Difficulty Rejected": 262144.0,
                    "Last Share Difficulty": 262144.0,
                    "Last Valid Work": 986,
                    "Device Hardware%": 0.0,
                    "Device Rejected%": 0.6275,
                    "Device Elapsed": 924,
                }
            ],
            "id": 1,
        },
        "rpc_pools": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 986,
                    "Code": 7,
                    "Msg": "3 Pool(s)",
                    "Description": "cgminer 4.11.1",
                }
            ],
            "POOLS": [
                {
                    "POOL": 0,
                    "URL": "stratum+tcp://stratum.pool.io:3333",
                    "Status": "Alive",
                    "Priority": 0,
                    "Quota": 1,
                    "Long Poll": "N",
                    "Getworks": 27,
                    "Accepted": 148,
                    "Rejected": 1,
                    "Works": 10199,
                    "Discarded": 0,
                    "Stale": 0,
                    "Get Failures": 0,
                    "Remote Failures": 0,
                    "User": "pool_username.real_worker",
                    "Last Share Time": 975,
                    "Diff1 Shares": 41775104,
                    "Proxy Type": "",
                    "Proxy": "",
                    "Difficulty Accepted": 38797312.0,
                    "Difficulty Rejected": 262144.0,
                    "Difficulty Stale": 0.0,
                    "Last Share Difficulty": 262144.0,
                    "Work Difficulty": 262144.0,
                    "Has Stratum": True,
                    "Stratum Active": True,
                    "Stratum URL": "stratum.pool.io",
                    "Stratum Difficulty": 262144.0,
                    "Has Vmask": True,
                    "Has GBT": False,
                    "Best Share": 19649871,
                    "Pool Rejected%": 0.6711,
                    "Pool Stale%": 0.0,
                    "Bad Work": 2,
                    "Current Block Height": 882588,
                    "Current Block Version": 536870912,
                },
                {
                    "POOL": 1,
                    "URL": "stratum+tcp://stratum.pool.io:3334",
                    "Status": "Alive",
                    "Priority": 1,
                    "Quota": 1,
                    "Long Poll": "N",
                    "Getworks": 2,
                    "Accepted": 0,
                    "Rejected": 0,
                    "Works": 0,
                    "Discarded": 0,
                    "Stale": 0,
                    "Get Failures": 0,
                    "Remote Failures": 0,
                    "User": "pool_username.real_worker",
                    "Last Share Time": 0,
                    "Diff1 Shares": 0,
                    "Proxy Type": "",
                    "Proxy": "",
                    "Difficulty Accepted": 0.0,
                    "Difficulty Rejected": 0.0,
                    "Difficulty Stale": 0.0,
                    "Last Share Difficulty": 0.0,
                    "Work Difficulty": 0.0,
                    "Has Stratum": True,
                    "Stratum Active": False,
                    "Stratum URL": "stratum.pool.io",
                    "Stratum Difficulty": 0.0,
                    "Has Vmask": True,
                    "Has GBT": False,
                    "Best Share": 0,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%": 0.0,
                    "Bad Work": 0,
                    "Current Block Height": 0,
                    "Current Block Version": 536870912,
                },
                {
                    "POOL": 2,
                    "URL": "stratum+tcp://stratum.pool.io:3335",
                    "Status": "Alive",
                    "Priority": 2,
                    "Quota": 1,
                    "Long Poll": "N",
                    "Getworks": 1,
                    "Accepted": 0,
                    "Rejected": 0,
                    "Works": 0,
                    "Discarded": 0,
                    "Stale": 0,
                    "Get Failures": 0,
                    "Remote Failures": 0,
                    "User": "pool_username.real_worker",
                    "Last Share Time": 0,
                    "Diff1 Shares": 0,
                    "Proxy Type": "",
                    "Proxy": "",
                    "Difficulty Accepted": 0.0,
                    "Difficulty Rejected": 0.0,
                    "Difficulty Stale": 0.0,
                    "Last Share Difficulty": 0.0,
                    "Work Difficulty": 16384.0,
                    "Has Stratum": True,
                    "Stratum Active": False,
                    "Stratum URL": "stratum.pool.io",
                    "Stratum Difficulty": 0.0,
                    "Has Vmask": True,
                    "Has GBT": False,
                    "Best Share": 0,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%": 0.0,
                    "Bad Work": 0,
                    "Current Block Height": 882586,
                    "Current Block Version": 536870916,
                },
            ],
            "id": 1,
        },
        "rpc_stats": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 986,
                    "Code": 70,
                    "Msg": "CGMiner stats",
                    "Description": "cgminer 4.11.1",
                }
            ],
            "STATS": [
                {
                    "STATS": 0,
                    "ID": "AVA100",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "MM ID0": "Ver[15-194-24102401_25462b2_9ddf522] DNA[020100008c699117] MEMFREE[1392832.1381104] NETFAIL[0 0 0 0 0 0 0 0] SYSTEMSTATU[Work: In Work, Hash Board: 3 ] Elapsed[975] BOOTBY[0x04.00000000] LW[714031] MH[0 0 0] DHW[0] HW[0] DH[1.299%] Temp[31] TMax[78] TAvg[70] Fan1[4275] Fan2[4282] FanR[49%] Vo[296] PS[0 1209 1187 297 3526 1188 3731] WALLPOWER[3731] PLL0[3346 2549 4722 13703] PLL1[2620 2291 4741 14668] PLL2[1777 2019 3849 16675] GHSspd[199241.07] DHspd[1.299%] GHSmm[201920.42] GHSavg[184007.00] WU[2570548.05] Freq[345.94] Led[0] MGHS[59459.52 61407.83 63139.66] MTmax[77 78 77] MTavg[69 70 71] MVavg[285.7 286.3 285.8] TA[480] Core[A3197S] PING[131] POWS[0] EEPROM[160 160 160] HASHS[0 0 0] POOLS[0] SoftOFF[0] ECHU[0 0 0] ECMM[0] SF0[300 318 339 360] SF1[300 318 339 360] SF2[300 318 339 360] PVT_T0[ 66  65  63  62  64  64  66  65  67  68  65  64  62  64  66  68  66  64  63  63  64  65  65  66  68  66  64  64  65  67  66  68  65  65  64  62  64  67  66  66  65  65  64  65  61  66  66  65  65  65  64  61  61  65  66  66  66  68  65  64  63  63  64  66  65  64  62  64  65  64  65  67  66  68  64  62  60  63  66  64  68  68  70  71  73  73  73  69  70  74  73  73  76  75  73  71  70  73  74  74  76  76  75  71  69  74  73  74  72  72  71  68  69  71  74  73  73  75  74  69  69  74  75  75  73  74  70  70  68  70  72  70  77  75  73  71  73  72  74  74  75  75  71  68  71  71  72  75  74  73  71  69  69  71  71  71  72  74  70  69] PVT_T1[ 65  66  63  62  62  63  66  66  65  65  63  64  65  66  65  66  66  66  65  66  62  64  66  66  67  68  65  63  65  66  66  68  67  68  65  66  66  67  66  66  66  66  65  65  67  66  66  66  68  68  66  65  66  67  69  69  67  67  68  66  63  66  67  68  67  67  66  65  64  68  68  68  68  66  66  64  64  65  66  67  70  71  73  71  78  76  74  71  71  71  77  76  77  76  74  70  71  73  76  78  77  77  73  71  71  73  74  77  76  75  73  69  70  72  73  76  77  77  71  69  70  72  75  75  74  76  73  69  70  71  73  74  75  76  72  70  71  71  74  76  74  75  72  70  69  71  73  76  76  76  71  70  69  71  73  74  75  74  71  67] PVT_T2[ 67  66  66  63  69  67  67  69  66  70  67  68  66  71  68  69  69  67  67  68  69  69  68  67  69  68  68  70  70  71  68  69  71  68  70  69  71  66  68  70  67  66  67  71  69  67  68  67  69  68  68  69  66  69  69  67  70  66  67  67  67  67  66  69  70  66  71  68  67  69  68  69  70  68  69  68  70  67  67  68  72  71  74  74  74  74  72  71  70  74  76  75  74  76  76  71  73  74  76  77  77  75  74  73  72  72  77  76  73  75  74  71  71  71  73  74  74  75  72  70  69  73  74  74  74  74  74  71  71  72  73  74  75  75  74  74  73  72  77  75  75  75  72  72  71  72  74  75  75  74  74  71  69  72  74  74  74  73  70  68] PVT_V0[293 292 291 290 290 292 294 295 290 289 291 290 291 292 291 291 288 288 290 290 292 292 289 290 289 288 289 289 287 290 291 291 286 286 286 287 288 289 289 287 290 290 290 290 290 292 291 292 289 291 291 291 291 291 289 288 291 290 290 289 292 294 291 290 290 290 291 291 289 290 290 289 288 288 287 287 290 289 290 294 288 283 280 279 282 282 282 282 277 276 278 281 277 281 283 283 281 279 279 280 279 280 280 280 283 281 281 282 283 284 285 286 281 279 282 283 281 279 279 278 286 281 279 278 283 283 283 281 285 284 281 281 282 280 280 280 278 279 281 278 283 283 283 285 279 281 283 282 280 278 281 285 281 283 284 285 286 285 281 281] PVT_V1[293 292 293 290 292 293 292 292 291 290 292 291 291 291 291 291 291 293 290 290 291 292 292 293 290 290 292 292 289 289 289 287 291 291 291 290 289 289 288 287 290 289 289 289 291 291 290 291 292 291 289 288 288 289 288 289 289 290 288 288 290 289 290 290 291 291 291 291 288 289 287 287 291 291 288 288 288 289 291 294 286 283 282 281 278 282 280 283 282 282 278 279 282 280 283 281 281 278 280 278 279 281 282 282 283 282 282 283 286 285 285 284 284 281 282 282 279 280 283 281 283 282 282 282 279 284 282 284 284 282 282 282 283 282 282 284 285 283 283 282 283 283 283 283 280 282 281 281 283 284 284 286 285 285 286 287 286 286 283 285] PVT_V2[294 291 292 289 289 291 290 290 287 287 290 289 288 290 290 289 288 288 288 288 286 288 286 287 286 286 286 286 286 288 286 286 287 285 290 288 288 289 290 288 288 289 288 289 289 290 288 288 287 287 286 285 290 290 290 288 287 289 290 290 288 289 288 288 288 289 289 289 292 291 288 288 290 289 287 286 284 289 291 294 291 289 285 280 285 285 287 287 283 283 285 285 284 284 281 284 281 284 279 283 279 288 284 283 281 283 281 281 284 284 284 281 283 282 282 284 281 284 288 285 280 284 282 283 285 286 284 285 283 281 281 281 278 281 280 276 284 280 281 284 285 286 286 288 281 281 280 279 285 283 280 280 284 286 283 283 287 286 283 284] MW[238147 238178 238124] MW0[22 19 17 14 17 21 21 22 20 13 25 20 22 22 23 27 22 20 18 26 16 20 16 23 19 22 17 21 16 21 23 18 22 23 25 17 25 15 21 22 24 16 11 23 10 17 21 22 22 16 14 18 23 20 17 22 23 17 24 17 21 21 19 19 17 26 17 22 23 17 25 27 23 20 26 25 19 19 29 27 21 24 16 21 20 10 26 18 17 18 30 21 18 22 22 21 23 23 22 13 24 16 18 27 20 25 23 24 21 23 22 21 25 31 11 24 15 18 21 18 21 17 26 18 15 22 29 20 16 21 17 17 15 18 30 24 25 22 21 14 25 22 28 20 27 16 25 22 13 23 23 20 19 21 22 25 17 16 23 17] MW1[23 21 23 18 13 31 21 25 18 18 21 19 23 17 24 23 22 21 22 23 19 20 22 15 25 27 22 18 16 22 19 24 13 27 20 6 25 20 22 24 17 19 17 27 17 16 30 25 27 29 16 22 23 25 29 20 27 18 22 20 19 22 22 21 23 25 18 27 21 14 20 23 19 28 17 25 19 24 23 22 22 25 26 19 25 28 21 16 19 23 18 15 17 26 20 15 27 21 19 18 25 30 24 20 17 28 29 28 15 20 15 27 20 21 21 30 30 26 17 13 19 15 17 24 24 21 25 19 25 17 24 22 24 10 19 22 23 23 20 23 20 21 25 15 21 17 22 19 19 21 21 22 27 16 18 14 26 24 19 16] MW2[24 16 20 17 22 25 21 28 20 13 14 25 21 25 18 29 17 18 24 17 22 18 23 25 17 29 33 26 30 23 19 24 35 24 14 14 24 28 24 28 27 28 23 26 27 30 21 30 24 20 17 37 12 24 22 33 20 14 21 33 30 16 20 26 19 20 18 24 16 21 15 21 26 22 25 15 19 17 29 21 19 23 20 28 15 25 20 16 25 9 25 22 23 20 16 25 25 20 26 26 22 31 26 24 16 21 34 31 20 32 26 20 13 21 21 11 31 17 17 15 23 22 21 20 22 21 13 21 16 20 28 18 22 29 15 16 19 14 25 24 17 23 16 20 24 18 20 18 18 26 24 21 23 17 16 19 21 25 26 19] CRC[0 0 0] COMCRC[0 0 0] FACOPTS0[] FACOPTS1[] FACOPTS2[] ATAOPTS0[--avalon10-freq 240:258:279:300 --avalon10-voltage-level 1180 --hash-asic 160] ATAOPTS1[--avalon10-freq 300:318:339:360 --avalon10-voltage-level 1188 --hash-asic 160] ATAOPTS2[--avalon10-freq 300:318:339:360 --avalon10-voltage-level 1188 --hash-asic 160 --power-level 0] ADJ[1] COP[0 0 0] MPO[3515] MVL[87] ATABD0[300 318 339 360] ATABD1[300 318 339 360] ATABD2[300 318 339 360] WORKMODE[1]",
                    "MM Count": 1,
                    "Smart Speed": 1,
                    "Voltage Level Offset": 0,
                    "Nonce Mask": 25,
                },
                {
                    "STATS": 1,
                    "ID": "POOL0",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "Pool Calls": 0,
                    "Pool Attempts": 0,
                    "Pool Wait": 0.0,
                    "Pool Max": 0.0,
                    "Pool Min": 99999999.0,
                    "Pool Av": 0.0,
                    "Work Had Roll Time": False,
                    "Work Can Roll": False,
                    "Work Had Expire": False,
                    "Work Roll Time": 0,
                    "Work Diff": 262144.0,
                    "Min Diff": 262144.0,
                    "Max Diff": 262144.0,
                    "Min Diff Count": 2,
                    "Max Diff Count": 2,
                    "Times Sent": 152,
                    "Bytes Sent": 26720,
                    "Times Recv": 181,
                    "Bytes Recv": 62897,
                    "Net Bytes Sent": 26720,
                    "Net Bytes Recv": 62897,
                },
                {
                    "STATS": 2,
                    "ID": "POOL1",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "Pool Calls": 0,
                    "Pool Attempts": 0,
                    "Pool Wait": 0.0,
                    "Pool Max": 0.0,
                    "Pool Min": 99999999.0,
                    "Pool Av": 0.0,
                    "Work Had Roll Time": False,
                    "Work Can Roll": False,
                    "Work Had Expire": False,
                    "Work Roll Time": 0,
                    "Work Diff": 0.0,
                    "Min Diff": 0.0,
                    "Max Diff": 0.0,
                    "Min Diff Count": 0,
                    "Max Diff Count": 0,
                    "Times Sent": 3,
                    "Bytes Sent": 289,
                    "Times Recv": 7,
                    "Bytes Recv": 4954,
                    "Net Bytes Sent": 289,
                    "Net Bytes Recv": 4954,
                },
                {
                    "STATS": 3,
                    "ID": "POOL2",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "Pool Calls": 0,
                    "Pool Attempts": 0,
                    "Pool Wait": 0.0,
                    "Pool Max": 0.0,
                    "Pool Min": 99999999.0,
                    "Pool Av": 0.0,
                    "Work Had Roll Time": False,
                    "Work Can Roll": False,
                    "Work Had Expire": False,
                    "Work Roll Time": 0,
                    "Work Diff": 16384.0,
                    "Min Diff": 16384.0,
                    "Max Diff": 16384.0,
                    "Min Diff Count": 1,
                    "Max Diff Count": 1,
                    "Times Sent": 3,
                    "Bytes Sent": 257,
                    "Times Recv": 6,
                    "Bytes Recv": 1583,
                    "Net Bytes Sent": 257,
                    "Net Bytes Recv": 1583,
                },
            ],
            "id": 1,
        },
        "rpc_estats": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 986,
                    "Code": 70,
                    "Msg": "CGMiner stats",
                    "Description": "cgminer 4.11.1",
                }
            ],
            "STATS": [
                {
                    "STATS": 0,
                    "ID": "AVA100",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "MM ID0": "Ver[15-194-24102401_25462b2_9ddf522] DNA[020100008c699117] MEMFREE[1392832.1381104] NETFAIL[0 0 0 0 0 0 0 0] SYSTEMSTATU[Work: In Work, Hash Board: 3 ] Elapsed[975] BOOTBY[0x04.00000000] LW[714031] MH[0 0 0] DHW[0] HW[0] DH[1.299%] Temp[31] TMax[78] TAvg[70] Fan1[4275] Fan2[4282] FanR[49%] Vo[296] PS[0 1209 1187 297 3526 1188 3731] WALLPOWER[3731] PLL0[3346 2549 4722 13703] PLL1[2620 2291 4741 14668] PLL2[1777 2019 3849 16675] GHSspd[199241.07] DHspd[1.299%] GHSmm[201920.42] GHSavg[184007.00] WU[2570548.05] Freq[345.94] Led[0] MGHS[59459.52 61407.83 63139.66] MTmax[77 78 77] MTavg[69 70 71] MVavg[285.7 286.3 285.8] TA[480] Core[A3197S] PING[131] POWS[0] EEPROM[160 160 160] HASHS[0 0 0] POOLS[0] SoftOFF[0] ECHU[0 0 0] ECMM[0] SF0[300 318 339 360] SF1[300 318 339 360] SF2[300 318 339 360] PVT_T0[ 66  65  63  62  64  64  66  65  67  68  65  64  62  64  66  68  66  64  63  63  64  65  65  66  68  66  64  64  65  67  66  68  65  65  64  62  64  67  66  66  65  65  64  65  61  66  66  65  65  65  64  61  61  65  66  66  66  68  65  64  63  63  64  66  65  64  62  64  65  64  65  67  66  68  64  62  60  63  66  64  68  68  70  71  73  73  73  69  70  74  73  73  76  75  73  71  70  73  74  74  76  76  75  71  69  74  73  74  72  72  71  68  69  71  74  73  73  75  74  69  69  74  75  75  73  74  70  70  68  70  72  70  77  75  73  71  73  72  74  74  75  75  71  68  71  71  72  75  74  73  71  69  69  71  71  71  72  74  70  69] PVT_T1[ 65  66  63  62  62  63  66  66  65  65  63  64  65  66  65  66  66  66  65  66  62  64  66  66  67  68  65  63  65  66  66  68  67  68  65  66  66  67  66  66  66  66  65  65  67  66  66  66  68  68  66  65  66  67  69  69  67  67  68  66  63  66  67  68  67  67  66  65  64  68  68  68  68  66  66  64  64  65  66  67  70  71  73  71  78  76  74  71  71  71  77  76  77  76  74  70  71  73  76  78  77  77  73  71  71  73  74  77  76  75  73  69  70  72  73  76  77  77  71  69  70  72  75  75  74  76  73  69  70  71  73  74  75  76  72  70  71  71  74  76  74  75  72  70  69  71  73  76  76  76  71  70  69  71  73  74  75  74  71  67] PVT_T2[ 67  66  66  63  69  67  67  69  66  70  67  68  66  71  68  69  69  67  67  68  69  69  68  67  69  68  68  70  70  71  68  69  71  68  70  69  71  66  68  70  67  66  67  71  69  67  68  67  69  68  68  69  66  69  69  67  70  66  67  67  67  67  66  69  70  66  71  68  67  69  68  69  70  68  69  68  70  67  67  68  72  71  74  74  74  74  72  71  70  74  76  75  74  76  76  71  73  74  76  77  77  75  74  73  72  72  77  76  73  75  74  71  71  71  73  74  74  75  72  70  69  73  74  74  74  74  74  71  71  72  73  74  75  75  74  74  73  72  77  75  75  75  72  72  71  72  74  75  75  74  74  71  69  72  74  74  74  73  70  68] PVT_V0[293 292 291 290 290 292 294 295 290 289 291 290 291 292 291 291 288 288 290 290 292 292 289 290 289 288 289 289 287 290 291 291 286 286 286 287 288 289 289 287 290 290 290 290 290 292 291 292 289 291 291 291 291 291 289 288 291 290 290 289 292 294 291 290 290 290 291 291 289 290 290 289 288 288 287 287 290 289 290 294 288 283 280 279 282 282 282 282 277 276 278 281 277 281 283 283 281 279 279 280 279 280 280 280 283 281 281 282 283 284 285 286 281 279 282 283 281 279 279 278 286 281 279 278 283 283 283 281 285 284 281 281 282 280 280 280 278 279 281 278 283 283 283 285 279 281 283 282 280 278 281 285 281 283 284 285 286 285 281 281] PVT_V1[293 292 293 290 292 293 292 292 291 290 292 291 291 291 291 291 291 293 290 290 291 292 292 293 290 290 292 292 289 289 289 287 291 291 291 290 289 289 288 287 290 289 289 289 291 291 290 291 292 291 289 288 288 289 288 289 289 290 288 288 290 289 290 290 291 291 291 291 288 289 287 287 291 291 288 288 288 289 291 294 286 283 282 281 278 282 280 283 282 282 278 279 282 280 283 281 281 278 280 278 279 281 282 282 283 282 282 283 286 285 285 284 284 281 282 282 279 280 283 281 283 282 282 282 279 284 282 284 284 282 282 282 283 282 282 284 285 283 283 282 283 283 283 283 280 282 281 281 283 284 284 286 285 285 286 287 286 286 283 285] PVT_V2[294 291 292 289 289 291 290 290 287 287 290 289 288 290 290 289 288 288 288 288 286 288 286 287 286 286 286 286 286 288 286 286 287 285 290 288 288 289 290 288 288 289 288 289 289 290 288 288 287 287 286 285 290 290 290 288 287 289 290 290 288 289 288 288 288 289 289 289 292 291 288 288 290 289 287 286 284 289 291 294 291 289 285 280 285 285 287 287 283 283 285 285 284 284 281 284 281 284 279 283 279 288 284 283 281 283 281 281 284 284 284 281 283 282 282 284 281 284 288 285 280 284 282 283 285 286 284 285 283 281 281 281 278 281 280 276 284 280 281 284 285 286 286 288 281 281 280 279 285 283 280 280 284 286 283 283 287 286 283 284] MW[238147 238178 238124] MW0[22 19 17 14 17 21 21 22 20 13 25 20 22 22 23 27 22 20 18 26 16 20 16 23 19 22 17 21 16 21 23 18 22 23 25 17 25 15 21 22 24 16 11 23 10 17 21 22 22 16 14 18 23 20 17 22 23 17 24 17 21 21 19 19 17 26 17 22 23 17 25 27 23 20 26 25 19 19 29 27 21 24 16 21 20 10 26 18 17 18 30 21 18 22 22 21 23 23 22 13 24 16 18 27 20 25 23 24 21 23 22 21 25 31 11 24 15 18 21 18 21 17 26 18 15 22 29 20 16 21 17 17 15 18 30 24 25 22 21 14 25 22 28 20 27 16 25 22 13 23 23 20 19 21 22 25 17 16 23 17] MW1[23 21 23 18 13 31 21 25 18 18 21 19 23 17 24 23 22 21 22 23 19 20 22 15 25 27 22 18 16 22 19 24 13 27 20 6 25 20 22 24 17 19 17 27 17 16 30 25 27 29 16 22 23 25 29 20 27 18 22 20 19 22 22 21 23 25 18 27 21 14 20 23 19 28 17 25 19 24 23 22 22 25 26 19 25 28 21 16 19 23 18 15 17 26 20 15 27 21 19 18 25 30 24 20 17 28 29 28 15 20 15 27 20 21 21 30 30 26 17 13 19 15 17 24 24 21 25 19 25 17 24 22 24 10 19 22 23 23 20 23 20 21 25 15 21 17 22 19 19 21 21 22 27 16 18 14 26 24 19 16] MW2[24 16 20 17 22 25 21 28 20 13 14 25 21 25 18 29 17 18 24 17 22 18 23 25 17 29 33 26 30 23 19 24 35 24 14 14 24 28 24 28 27 28 23 26 27 30 21 30 24 20 17 37 12 24 22 33 20 14 21 33 30 16 20 26 19 20 18 24 16 21 15 21 26 22 25 15 19 17 29 21 19 23 20 28 15 25 20 16 25 9 25 22 23 20 16 25 25 20 26 26 22 31 26 24 16 21 34 31 20 32 26 20 13 21 21 11 31 17 17 15 23 22 21 20 22 21 13 21 16 20 28 18 22 29 15 16 19 14 25 24 17 23 16 20 24 18 20 18 18 26 24 21 23 17 16 19 21 25 26 19] CRC[0 0 0] COMCRC[0 0 0] FACOPTS0[] FACOPTS1[] FACOPTS2[] ATAOPTS0[--avalon10-freq 240:258:279:300 --avalon10-voltage-level 1180 --hash-asic 160] ATAOPTS1[--avalon10-freq 300:318:339:360 --avalon10-voltage-level 1188 --hash-asic 160] ATAOPTS2[--avalon10-freq 300:318:339:360 --avalon10-voltage-level 1188 --hash-asic 160 --power-level 0] ADJ[1] COP[0 0 0] MPO[3515] MVL[87] ATABD0[300 318 339 360] ATABD1[300 318 339 360] ATABD2[300 318 339 360] WORKMODE[1]",
                    "MM Count": 1,
                    "Smart Speed": 1,
                    "Voltage Level Offset": 0,
                    "Nonce Mask": 25,
                },
                {
                    "STATS": 1,
                    "ID": "POOL0",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "Pool Calls": 0,
                    "Pool Attempts": 0,
                    "Pool Wait": 0.0,
                    "Pool Max": 0.0,
                    "Pool Min": 99999999.0,
                    "Pool Av": 0.0,
                    "Work Had Roll Time": False,
                    "Work Can Roll": False,
                    "Work Had Expire": False,
                    "Work Roll Time": 0,
                    "Work Diff": 262144.0,
                    "Min Diff": 262144.0,
                    "Max Diff": 262144.0,
                    "Min Diff Count": 2,
                    "Max Diff Count": 2,
                    "Times Sent": 152,
                    "Bytes Sent": 26720,
                    "Times Recv": 181,
                    "Bytes Recv": 62897,
                    "Net Bytes Sent": 26720,
                    "Net Bytes Recv": 62897,
                },
                {
                    "STATS": 2,
                    "ID": "POOL1",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "Pool Calls": 0,
                    "Pool Attempts": 0,
                    "Pool Wait": 0.0,
                    "Pool Max": 0.0,
                    "Pool Min": 99999999.0,
                    "Pool Av": 0.0,
                    "Work Had Roll Time": False,
                    "Work Can Roll": False,
                    "Work Had Expire": False,
                    "Work Roll Time": 0,
                    "Work Diff": 0.0,
                    "Min Diff": 0.0,
                    "Max Diff": 0.0,
                    "Min Diff Count": 0,
                    "Max Diff Count": 0,
                    "Times Sent": 3,
                    "Bytes Sent": 289,
                    "Times Recv": 7,
                    "Bytes Recv": 4954,
                    "Net Bytes Sent": 289,
                    "Net Bytes Recv": 4954,
                },
                {
                    "STATS": 3,
                    "ID": "POOL2",
                    "Elapsed": 975,
                    "Calls": 0,
                    "Wait": 0.0,
                    "Max": 0.0,
                    "Min": 99999999.0,
                    "Pool Calls": 0,
                    "Pool Attempts": 0,
                    "Pool Wait": 0.0,
                    "Pool Max": 0.0,
                    "Pool Min": 99999999.0,
                    "Pool Av": 0.0,
                    "Work Had Roll Time": False,
                    "Work Can Roll": False,
                    "Work Had Expire": False,
                    "Work Roll Time": 0,
                    "Work Diff": 16384.0,
                    "Min Diff": 16384.0,
                    "Max Diff": 16384.0,
                    "Min Diff Count": 1,
                    "Max Diff Count": 1,
                    "Times Sent": 3,
                    "Bytes Sent": 257,
                    "Times Recv": 6,
                    "Bytes Recv": 1583,
                    "Net Bytes Sent": 257,
                    "Net Bytes Recv": 1583,
                },
            ],
            "id": 1,
        },
    }
}


class TestAvalonMiners(unittest.IsolatedAsyncioTestCase):
    @patch("pyasic.rpc.base.BaseMinerRPCAPI._send_bytes")
    async def test_all_data_gathering(self, mock_send_bytes):
        mock_send_bytes.raises = APIError()
        for m_type in data:
            gathered_data = {}
            miner = m_type("127.0.0.1")
            for data_name in fields(miner.data_locations):
                if data_name.name == "config":
                    # skip
                    continue
                data_func = getattr(miner.data_locations, data_name.name)
                fn_args = data_func.kwargs
                args_to_send = {k.name: data[m_type][k.name] for k in fn_args}
                function = getattr(miner, data_func.cmd)
                gathered_data[data_name.name] = await function(**args_to_send)

            result = MinerData(
                ip=str(miner.ip),
                device_info=miner.device_info,
                expected_chips=(
                    miner.expected_chips * miner.expected_hashboards
                    if miner.expected_chips is not None
                    else 0
                ),
                expected_hashboards=miner.expected_hashboards,
                expected_fans=miner.expected_fans,
                hashboards=[
                    HashBoard(slot=i, expected_chips=miner.expected_chips)
                    for i in range(miner.expected_hashboards)
                ],
            )
            for item in gathered_data:
                if gathered_data[item] is not None:
                    setattr(result, item, gathered_data[item])

            self.assertEqual(result.mac, "12:34:56:78:90:12")
            self.assertEqual(result.api_ver, "3.7")
            self.assertEqual(result.fw_ver, "4.11.1")
            self.assertEqual(round(result.hashrate.into(SHA256Unit.TH)), 184)
            self.assertEqual(
                result.fans,
                [Fan(speed=4275), Fan(speed=4282)],
            )
            self.assertEqual(result.total_chips, result.expected_chips)
            self.assertEqual(
                set([str(p.url) for p in result.pools]), set(p["url"] for p in POOLS)
            )
            self.assertEqual(result.wattage, 3731)
            self.assertEqual(result.wattage_limit, 3515)
