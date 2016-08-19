#!/bin/bash

echo '== PYTHON VERSION =='
echo `which python`
echo `python --version`

echo ''
echo '== PIP VERSION AND LIBS =='
echo `which pip`
echo `pip --version`
echo "`pip list --no-index`"

echo ''
echo '== GIT REPO INFO =='
echo `git describe --tags`
echo `git rev-parse HEAD`
