"""
SAMPLE CONFIG
-------------------
{
    "format": {
        "version": "1.2+", # -> (default = "1.2+", str, (bos: format.version))
        "model": "Antminer S9", # -> (default = "Antminer S9", str, (bos: format.model))
        "generator": "upstream_config_util", # -> (hidden, always = "upstream_config_util", str, (bos: format.generator))
        "timestamp": 1606842000, # -> (hidden, always = int(time.time()) (current unix time), int, (bos: format.timestamp))
    },
    "temperature": {
        "mode": "auto", # -> (default = "auto", str["auto", "manual", "disabled"], (bos: temp_control.mode))
        "target": 70.0, # -> (default = 70.0, float, (bos: temp_control.target_temp))
        "hot": 80.0, # -> (default = 80.0, float, (bos: temp_control.hot_temp))
        "danger": 90.0, # -> (default = 90.0, float, (bos: temp_control.dangerous_temp))
    },
    "fans": { # -> (optional, required if temperature["mode"] == "disabled", (bos: fan_control))
        "min_fans": 1, # -> (default = 1, int, (bos: fan_control.min_fans))
        "speed": 100, # -> (default = 100, 0 < int < 100, (bos: fan_control.speed))
    },
    "asicboost": True, # -> (default = True, bool, (bos : hash_chain_global.asic_boost))
    "pool_groups": [
        {
            "group_name": "Upstream", # -> (default = "group_{index}" (group_0), str, (bos: group.[index].name))
            "quota": 1, # -> (default = 1, int, (bos: group.[index].quota))
            "pools": [
                {
                    "url": "stratum+tcp://stratum.slushpool.com:3333", # -> (str, (bos: group.[index].pool.[index].url))
                    "username": "UpstreamDataInc.test", # -> (str, (bos: group.[index].pool.[index].user))
                    "password": "123", # -> (str, (bos: group.[index].pool.[index].password))
                },
                {
                    "url": "stratum+tcp://us-east.stratum.slushpool.com:3333", # -> (str, (bos: group.[index].pool.[index].url))
                    "username": "UpstreamDataInc.test", # -> (str, (bos: group.[index].pool.[index].user))
                    "password": "123", # -> (str, (bos: group.[index].pool.[index].password))
                },
                {
                    "url": "stratum+tcp://ca.stratum.slushpool.com:3333", # -> (str, (bos: group.[index].pool.[index].url))
                    "username": "UpstreamDataInc.test", # -> (str, (bos: group.[index].pool.[index].user))
                    "password": "123", # -> (str, (bos: group.[index].pool.[index].password))
                },
            ]
        },
        {
            "group_name": "Upstream2", # -> (default = "group_{index}" (group_1), str, (bos: group.[index].name))
            "quota": 4, # -> (default = 1, int, (bos: group.[index].quota))
            "pools": [
                {
                    "url": "stratum+tcp://stratum.slushpool.com:3333", # -> (str, (bos: group.[index].pool.[index].url))
                    "username": "UpstreamDataTesting.test", # -> (str, (bos: group.[index].pool.[index].user))
                    "password": "123", # -> (str, (bos: group.[index].pool.[index].password))
                },
                {
                    "url": "stratum+tcp://us-east.stratum.slushpool.com:3333", # -> (str, (bos: group.[index].pool.[index].url))
                    "username": "UpstreamDataTesting.test", # -> (str, (bos: group.[index].pool.[index].user))
                    "password": "123", # -> (str, (bos: group.[index].pool.[index].password))
                },
                {
                    "url": "stratum+tcp://ca.stratum.slushpool.com:3333", # -> (str, (bos: group.[index].pool.[index].url))
                    "username": "UpstreamDataTesting.test", # -> (str, (bos: group.[index].pool.[index].user))
                    "password": "123", # -> (str, (bos: group.[index].pool.[index].password))
                },
            ]
        },
    ],
    "autotuning": {
        "enabled": True, # -> (default = True, bool), (bos: autotuning.enabled)
        "wattage": 900, # -> (default = 900, bool, (bos: autotuning.psu_power_limit))
    },
    "power_scaling": {
        "enabled": False, # -> (default = False, bool, (bos: power_scaling.enabled))
        "power_step": 100, # -> (default = 100, int, (bos: power_scaling.power_step))
        "min_psu_power_limit": 800, # -> (default = 800, int, (bos: power_scaling.min_psu_power_limit))
        "shutdown_enabled": True, # -> (default = False, bool, (bos: power_scaling.shutdown_enabled))
        "shutdown_duration": 3.0, # -> (default = 3.0, float, (bos: power_scaling.shutdown_duration))
    }
}
"""