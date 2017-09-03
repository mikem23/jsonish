#!/bin/bash

echo "== Python 2 =="
coverage erase
coverage run --source jsonish /usr/bin/nosetests; coverage report
echo $'\n== Python 3 =='
coverage3 erase
coverage3 run --source jsonish /usr/bin/nosetests-3; coverage report

