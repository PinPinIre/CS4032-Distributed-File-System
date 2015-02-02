#!/bin/bash

mkdir -p ClientFiles
mkdir -p Database
mkdir -p DirectoryServerFiles/8006
mkdir -p DirectoryServerFiles/8009
mkdir -p DirectoryServerFiles/8010

python src/Servers/directoryServer.py 8005 &
python src/Servers/lockServer.py 8007 &
python src/Servers/fileServer.py 8006 &
python src/Servers/fileServer.py 8009 &
python src/Servers/fileServer.py 8010 &

python src/setup.py
