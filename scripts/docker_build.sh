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

docker pull adieyal/wazimap-ng || true
cp ../Dockerfile.build Dockerfile
docker build -t adieyal/wazimap-ng:$TAG .

docker push adieyal/wazimap-ng

cd ..
rm -rf build
