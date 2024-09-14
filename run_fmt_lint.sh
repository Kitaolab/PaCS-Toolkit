#!/bin/bash
set -e
pip install -r requirements_dev.txt
pysen run format
pysen run lint
