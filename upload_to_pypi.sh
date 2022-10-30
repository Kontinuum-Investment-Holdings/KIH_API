#!/bin/bash

rm -rf dist/*
python3 setup.py sdist
twine upload -u __token__ -p $PYPI_API_TOKEN dist/*