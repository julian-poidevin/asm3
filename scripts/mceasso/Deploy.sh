#!/bin/bash
cd ../..
make all
make dist
cd build/
dpkg -i *.deb
sudo apt-get install -f
service sheltermanager3 stop
sudo cp /etc/asm3.conf.bak /etc/asm3.conf
service sheltermanager3 restart