#!/bin/sh

# Make sure "comp coil on" relay is set to 0
curl localhost:8000/data/cardD
echo ""
curl -s -X POST -H "Content-type: application/json" -d '{"cardD":{"channel'21'":0}}' http://localhost:8000/write
curl localhost:8000/data/cardD
echo ""
sleep 1

# Set "comp coil off" relay to 1, wait 3 seconds, then set to 0
curl -s -X POST -H "Content-type: application/json" -d '{"cardD":{"channel'20'":1}}' http://localhost:8000/write
curl localhost:8000/data/cardD
echo ""
sleep 3
curl -s -X POST -H "Content-type: application/json" -d '{"cardD":{"channel'20'":0}}' http://localhost:8000/write
curl localhost:8000/data/cardD
echo ""

echo "Comp Coils are now set to 'off'"
