set -euo pipefail

mkdir -p build
cd build
cp ../Dockerfile.build ./Dockerfile
cp ../requirements.txt .
cp -R ../scripts .

docker pull adieyal/wazimap-ng || true

docker build -t adieyal/wazimap-ng .

docker push adieyal/wazimap-ng

cd ..
rm -rf build
