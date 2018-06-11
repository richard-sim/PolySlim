# PolySlim
Blender addon for mesh decimation using the qslim algorithm. Tested on Blender 2.79 on MacOS, Linux, and Windows. Unlike most Blender addons, PolySlim contains platform-specific shared libraries.

## Installing

You can obtain pre-built versions of PolySlim for MacOS, Linux, and Windows from the [releases|Releases tab] of this repository.

### Windows

Download the latest .zip release and install via User Preferences > Add-ons > Install add-on from file. The Visual Studio 2017 x64 redistributable will also need to be installed: [Microsoft Visual C++ Redistributable for Visual Studio 2017](https://go.microsoft.com/fwlink/?LinkId=746572).

### MacOS and Linux

Download the latest .tar.gz release (**not** the .zip) and manually uncompress it into your Blender user settings directory. This is necessary as there are symlinks between files on these platforms, and .zip doesn't support that (unfortunately Blender doesn't support installing .tar.gz addons via the User Preferences dialog).

#### MacOS User Settings Location

~/Library/Application Support/Blender/2.79/scripts/addons/

#### Linux User Settings Location

~/.config/blender/2.79/scripts/addons/

## Building

You will need a recent CMake and Boost installed. Tested with GCC and clang on MacOS with CMake 3.9.4 and Boost 1.64, GCC on Linux with CMake 3.11.3 and Boost 1.67, and Visual Studio 2017 on Windows with CMake 3.11.3 and Boost 1.67.

MacOS and Linux:
  cd path/to/PolySlim
  mkdir build
  cd build
  cmake ..
  make

Windows
  cd path\to\PolySlim
  mkdir build
  cd build
  cmake -G "Visual Studio 15 2017 Win64" -DBOOST_ROOT=C:\local\boost_1_67_0 ..
  msbuild polyslim.sln /p:Configuration=Release

## Dependencies

This repository contains submodules (and its submodules contain their own submodules too!), so make sure you clone the repository recursively if you intend on building from source.
