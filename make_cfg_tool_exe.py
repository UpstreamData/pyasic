"""
Make a build of the config tool.

Usage: make_config_tool.py build

The build will show up in the build directory.
"""
import datetime
import sys
import os
from cx_Freeze import setup, Executable
from setuptools import find_packages

base = None
if sys.platform == "win32":
    base = "Win32GUI"

version = datetime.datetime.now()
version = version.strftime("%y.%m.%d")


setup(
    name="UpstreamCFGUtil.exe",
    version=version,
    description="Upstream Data Config Utility Build",
    options={
        "build_exe": {
            "build_exe": f"{os.getcwd()}\\build\\UpstreamCFGUtil-{version}-{sys.platform}\\",
            "include_files": [
                os.path.join(os.getcwd(), "settings/settings.toml"),
                os.path.join(os.getcwd(), "static/CFG-Util-README.md"),
            ],
            "excludes": ["tests", "tools.web_testbench", "tools.web_monitor"],
        },
    },
    executables=[
        Executable(
            "config_tool.py",
            base=base,
            icon="icon.ico",
            target_name="UpstreamCFGUtil.exe",
        )
    ],
)
