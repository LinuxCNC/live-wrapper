#!/bin/sh

pylint --disable="E0611" bin/lwr lbng
pep8 bin/lbng lbng

