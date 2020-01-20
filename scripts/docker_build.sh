set -euo pipefail

rm -rf build
git clone -l . ./build
cd build

docker pull adieyal/wazimap-ng || true
cp ../Dockerfile.build Dockerfile
docker build -t adieyal/wazimap-ng:latest .

docker push adieyal/wazimap-ng

cd ..
rm -rf build
