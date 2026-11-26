#!/bin/sh
cd "$(dirname "$0")"
exec java -jar smart-proposal.jar serve "${1:-127.0.0.1}" "${2:-8080}"
