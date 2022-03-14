"""
Make a build of the board tool.

Usage: make_board_tool_exe.py build

The build will show up in the build directory.
"""
import datetime
import sys
import os
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

version = datetime.datetime.now()
version = version.strftime("%y.%m.%d")
print(version)


setup(name="UpstreamBoardUtil.exe",
      version=version,
      description="Upstream Data Board Utility Build",
      options={
          "build_exe": {
              "build_exe": f"{os.getcwd()}\\build\\board_util\\UpstreamBoardUtil-{version}-{sys.platform}\\",
              "include_msvcr": True,
              "add_to_path": True
          },
      },
      executables=[Executable(
          "board_util.py",
          base=base,
          icon="icon.ico",
          target_name="UpstreamBoardUtil.exe"
      )]
      )
