#!/bin/bash
curl -i -X POST -H 'Content-Type: application/json' -d "{\"method\":\"$2\", \"params\": $3, \"jsonrpc\":\"2.0\", \"id\": 0}" $1
