# PolySlim
Blender addon for mesh decimation using the qslim algorithm

## Building

You will need CMake and Boost installed.

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
