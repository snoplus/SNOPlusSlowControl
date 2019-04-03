#!/bin/sh

# Must supply which XL3 as an argument
if [ $# -eq 0 ]
  then
      echo "Supply XL3 number as an argument!"

else
XL3=`expr $1`

echo "Resetting XL3 $1"

curl -s -X POST -H "Content-type: application/json" -d '{"cardD":{"channel'`echo $XL3`'":1}}' http://localhost:8000/write
curl localhost:8000/data/cardD
echo ""
sleep 3
curl -s -X POST -H "Content-type: application/json" -d '{"cardD":{"channel'`echo $XL3`'":0}}' http://localhost:8000/write
curl localhost:8000/data/cardD
echo ""
fi
