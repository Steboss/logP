#!/bin/bash
cd free
cp -aL template run001
cd run001
bash runme.sh
cd ../../
cd cyc
cp -a template run001
cd run001
bash runme.sh
cd ../../
cd vac
cp -a template run001
cd run001
bash runme.sh
cd ../../
