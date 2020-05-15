SKIP_CONTAINER_PUSH=$2

if [ $# -eq 0 ]
  then
    TAG="latest"

else
   TAG=$1
fi

set -euo pipefail

rm -rf build
git clone -l . ./build
cd build

rm -rf .git

docker pull adieyal/wazimap-ng:$TAG || true
cp ../Dockerfile.build Dockerfile
docker build -t adieyal/wazimap-ng:$TAG .
docker push adieyal/wazimap-ng:$TAG

cd ..
rm -rf build
