#!/bin/bash
#
source venv/bin/activate
python -m src.web_server.run --host 0.0.0.0 --port 8080
