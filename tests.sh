#!/bin/sh

pylint --disable="E0611" bin/lwr lwr
pep8 bin/lwr lwr

