#!/usr/bin/env python
import os

from snakepit import server

server.run(
    host=os.environ.get('SNAKEPIT_HOST', None),
    port=int(os.environ.get('SNAKEPIT_PORT', 8000)),
    debug=bool(os.environ.get('SNAKEPIT_DEBUG', True)),
)
