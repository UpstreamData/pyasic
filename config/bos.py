import time
import yaml
import toml


async def bos_config_convert(config: dict):
    out_config = {}
    for opt in config:
        if opt == "format":
            out_config["format"] = config[opt]
            out_config["format"]["generator"] = "upstream_config_util"
            out_config["format"]["timestamp"] = int(time.time())
        elif opt == "temp_control":
            out_config["temperature"] = {}
            if "mode" in config[opt].keys():
                out_config["temperature"]["mode"] = config[opt]["mode"]
            else:
                out_config["temperature"]["mode"] = "auto"

            if "target_temp" in config[opt].keys():
                out_config["temperature"]["target"] = config[opt]["target_temp"]
            else:
                out_config["temperature"]["target"] = 70.0

            if "hot_temp" in config[opt].keys():
                out_config["temperature"]["hot"] = config[opt]["hot_temp"]
            else:
                out_config["temperature"]["hot"] = 80.0

            if "dangerous_temp" in config[opt].keys():
                out_config["temperature"]["danger"] = config[opt]["dangerous_temp"]
            else:
                out_config["temperature"]["danger"] = 90.0
        elif opt == "fan_control":
            out_config["fans"] = {}
            if "min_fans" in config[opt].keys():
                out_config["fans"]["min_fans"] = config[opt]["min_fans"]
            else:
                out_config["fans"]["min_fans"] = 1
            if "speed" in config[opt].keys():
                out_config["fans"]["speed"] = config[opt]["speed"]
            else:
                out_config["fans"]["speed"] = 100
        elif opt == "group":
            out_config["pool_groups"] = [{} for _item in range(len(config[opt]))]
            for idx in range(len(config[opt])):
                out_config["pool_groups"][idx]["pools"] = []
                out_config["pool_groups"][idx] = {}
                if "name" in config[opt][idx].keys():
                    out_config["pool_groups"][idx]["group_name"] = config[opt][idx][
                        "name"
                    ]
                else:
                    out_config["pool_groups"][idx]["group_name"] = f"group_{idx}"
                if "quota" in config[opt][idx].keys():
                    out_config["pool_groups"][idx]["quota"] = config[opt][idx]["quota"]
                else:
                    out_config["pool_groups"][idx]["quota"] = 1
                out_config["pool_groups"][idx]["pools"] = [
                    {} for _item in range(len(config[opt][idx]["pool"]))
                ]
                for pool_idx in range(len(config[opt][idx]["pool"])):
                    out_config["pool_groups"][idx]["pools"][pool_idx]["url"] = config[
                        opt
                    ][idx]["pool"][pool_idx]["url"]
                    out_config["pool_groups"][idx]["pools"][pool_idx][
                        "username"
                    ] = config[opt][idx]["pool"][pool_idx]["user"]
                    out_config["pool_groups"][idx]["pools"][pool_idx][
                        "password"
                    ] = config[opt][idx]["pool"][pool_idx]["password"]
        elif opt == "autotuning":
            out_config["autotuning"] = {}
            if "enabled" in config[opt].keys():
                out_config["autotuning"]["enabled"] = config[opt]["enabled"]
            else:
                out_config["autotuning"]["enabled"] = True
            if "psu_power_limit" in config[opt].keys():
                out_config["autotuning"]["wattage"] = config[opt]["psu_power_limit"]
            else:
                out_config["autotuning"]["wattage"] = 900
        elif opt == "power_scaling":
            out_config["power_scaling"] = {}
            if "enabled" in config[opt].keys():
                out_config["power_scaling"]["enabled"] = config[opt]["enabled"]
            else:
                out_config["power_scaling"]["enabled"] = False
            if "power_step" in config[opt].keys():
                out_config["power_scaling"]["power_step"] = config[opt]["power_step"]
            else:
                out_config["power_scaling"]["power_step"] = 100
            if "min_psu_power_limit" in config[opt].keys():
                out_config["power_scaling"]["min_psu_power_limit"] = config[opt][
                    "min_psu_power_limit"
                ]
            else:
                out_config["power_scaling"]["min_psu_power_limit"] = 800
            if "shutdown_enabled" in config[opt].keys():
                out_config["power_scaling"]["shutdown_enabled"] = config[opt][
                    "shutdown_enabled"
                ]
            else:
                out_config["power_scaling"]["shutdown_enabled"] = False
            if "shutdown_duration" in config[opt].keys():
                out_config["power_scaling"]["shutdown_duration"] = config[opt][
                    "shutdown_duration"
                ]
            else:
                out_config["power_scaling"]["shutdown_duration"] = 3.0
    return yaml.dump(out_config, sort_keys=False)


async def general_config_convert_bos(yaml_config):
    config = yaml.load(yaml_config, Loader=yaml.SafeLoader)
    out_config = {}
    for opt in config:
        if opt == "format":
            out_config["format"] = config[opt]
            out_config["format"]["generator"] = "upstream_config_util"
            out_config["format"]["timestamp"] = int(time.time())
        elif opt == "temperature":
            out_config["temp_control"] = {}
            if "mode" in config[opt].keys():
                out_config["temp_control"]["mode"] = config[opt]["mode"]
            else:
                out_config["temp_control"]["mode"] = "auto"

            if "target" in config[opt].keys():
                out_config["temp_control"]["target_temp"] = config[opt]["target"]
            else:
                out_config["temp_control"]["target_temp"] = 70.0

            if "hot" in config[opt].keys():
                out_config["temp_control"]["hot_temp"] = config[opt]["hot"]
            else:
                out_config["temp_control"]["hot_temp"] = 80.0

            if "danger" in config[opt].keys():
                out_config["temp_control"]["dangerous_temp"] = config[opt]["danger"]
            else:
                out_config["temp_control"]["dangerous_temp"] = 90.0
        elif opt == "fans":
            out_config["fan_control"] = {}
            if "min_fans" in config[opt].keys():
                out_config["fan_control"]["min_fans"] = config[opt]["min_fans"]
            else:
                out_config["fan_control"]["min_fans"] = 1
            if "speed" in config[opt].keys():
                out_config["fan_control"]["speed"] = config[opt]["speed"]
            else:
                out_config["fan_control"]["speed"] = 100
        elif opt == "pool_groups":
            out_config["group"] = [{} for _item in range(len(config[opt]))]
            for idx in range(len(config[opt])):
                out_config["group"][idx]["pools"] = []
                out_config["group"][idx] = {}
                if "group_name" in config[opt][idx].keys():
                    out_config["group"][idx]["name"] = config[opt][idx]["group_name"]
                else:
                    out_config["group"][idx]["name"] = f"group_{idx}"
                if "quota" in config[opt][idx].keys():
                    out_config["group"][idx]["quota"] = config[opt][idx]["quota"]
                else:
                    out_config["group"][idx]["quota"] = 1
                out_config["group"][idx]["pool"] = [
                    {} for _item in range(len(config[opt][idx]["pools"]))
                ]
                for pool_idx in range(len(config[opt][idx]["pools"])):
                    out_config["group"][idx]["pool"][pool_idx]["url"] = config[opt][
                        idx
                    ]["pools"][pool_idx]["url"]
                    out_config["group"][idx]["pool"][pool_idx]["user"] = config[opt][
                        idx
                    ]["pools"][pool_idx]["username"]
                    out_config["group"][idx]["pool"][pool_idx]["password"] = config[
                        opt
                    ][idx]["pools"][pool_idx]["password"]
        elif opt == "autotuning":
            out_config["autotuning"] = {}
            if "enabled" in config[opt].keys():
                out_config["autotuning"]["enabled"] = config[opt]["enabled"]
            else:
                out_config["autotuning"]["enabled"] = True
            if "wattage" in config[opt].keys():
                out_config["autotuning"]["psu_power_limit"] = config[opt]["wattage"]
            else:
                out_config["autotuning"]["psu_power_limit"] = 900
        elif opt == "power_scaling":
            out_config["power_scaling"] = {}
            if "enabled" in config[opt].keys():
                out_config["power_scaling"]["enabled"] = config[opt]["enabled"]
            else:
                out_config["power_scaling"]["enabled"] = False
            if "power_step" in config[opt].keys():
                out_config["power_scaling"]["power_step"] = config[opt]["power_step"]
            else:
                out_config["power_scaling"]["power_step"] = 100
            if "min_psu_power_limit" in config[opt].keys():
                out_config["power_scaling"]["min_psu_power_limit"] = config[opt][
                    "min_psu_power_limit"
                ]
            else:
                out_config["power_scaling"]["min_psu_power_limit"] = 800
            if "shutdown_enabled" in config[opt].keys():
                out_config["power_scaling"]["shutdown_enabled"] = config[opt][
                    "shutdown_enabled"
                ]
            else:
                out_config["power_scaling"]["shutdown_enabled"] = False
            if "shutdown_duration" in config[opt].keys():
                out_config["power_scaling"]["shutdown_duration"] = config[opt][
                    "shutdown_duration"
                ]
            else:
                out_config["power_scaling"]["shutdown_duration"] = 3.0
    return out_config
