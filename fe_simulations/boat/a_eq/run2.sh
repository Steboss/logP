#!/bin/bash
cd free
cp -aL template run002
cd run002
bash runme.sh
cd ../../
cd cyc
cp -a template run002
cd run002
bash runme.sh
cd ../../
cd vac
cp -a template run002
cd run002
bash runme.sh
cd ../../
