# Installing and Using the iLink Test Tool #
#### **_Note: This can only be executed and run if you have the required hardware. You will also need to be connected to the UVC_**

### Step 1: Install the needed libraries and dependencies for local testing
#### Pre-requisite: Clone the repo (git@bitbucket.org:glaukos-east/ilink-test-tool.git) and cd into the ilink-test-tool repo first before running the commands below.

```
sudo apt install protobuf-compiler=3.21.12-8.2ubuntu0.2

sudo apt install python3-tk=3.12.3-0ubuntu1

pip install protobuf==6.31.1 grpcio-tools==1.74.0

git clone git@bitbucket.org:glaukos-east/nanopb.git

ln -s nanopb/generator/protoc-gen-nanopb /usr/local/bin/protoc-gen-nanopb

ln -s nanopb/generator/protoc /usr/local/bin/nanopb

chmod +x neo_pbc_api/build_protobufs.sh

cd ilink-test-tool/neo_pbc_api

./build_protobufs.sh
```

### NOTE: TBD EXACT STEPS FOR BUILDING UVC, ADDING POINTER TO README.md FOR NOW
```
Follow the steps of the https://bitbucket.org/glaukos-east/neo_uvc/src/main/readme.md to setup neo_uvc
```

### Step 2: Install the needed libraries and dependencies
```
pip install -r requirements.txt
```

### Step 3a: Use the linux executable from local environment
```
pyinstaller --onefile --clean \
    --hidden-import=google.protobuf \
    --hidden-import=google.protobuf.internal \
    --hidden-import=google.protobuf.internal.builder \
    --add-data "./neo_pbc_api/source/python/pbc_pb2.py:." \
    --add-data "source:source" --add-data "source/.env:." \
    --add-data "source/uvc/UvcServices_pb2.py:." 
    source/ilink_test_tool.py
```

### Step 3b: Use the linux GUI executable from local environment
```
pyinstaller --onefile --clean \
    --hidden-import=cv2 \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=google.protobuf \
    --hidden-import=google.protobuf.any_pb2 \
    --hidden-import=google.protobuf.internal \
    --hidden-import=google.protobuf.internal.builder \
    --add-data "source/resources:resources" \
    --add-data "./neo_pbc_api/source/python/pbc_pb2.py:." \
    --add-data "./neo-hbc-api/source/python/hbc_pb2.py:." \
    --add-data "source/uvc/UvcServices_pb2.py:." \
    --add-data "source/.env:." \
    --add-data "source:source" \
    source/ilink_test_tool_gui.py
```

### Note: To create the protobuf file in the expected folder, run the below script (Use this command once AUR-25 is fixed).
```
protoc \
  --python_out=./neo-uvc-uic-api/source/python \
  --proto_path=./neo-uvc-uic-api/Src \
  ./neo-uvc-uic-api/Src/UvcServices.proto
```

### Note: To create the protobuf file in the expected folder, run the below script (Use this otherwise).
```
protoc \
  --python_out=./source/uvc \
  --proto_path=./neo-uvc-uic-api/Src \
  ./neo-uvc-uic-api/Src/UvcServices.proto
```

### Note: Current settings to update for uvc.json for the ilink test tool to work
### This config is specific to the S/W lab's camera setup, please use pylon viewer to find the best config values for your setup.
```
  "narrowCamera.acquisitionMode": "timed"
  "narrowCamera.exposure": 15000
  "narrowCamera.left.ROI.height": 1544
  "narrowCamera.left.ROI.offsetX": 8
  "narrowCamera.left.ROI.offsetY": 4
  "narrowCamera.left.ROI.width": 2064
  "narrowCamera.left.gain": 25
  "narrowCamera.maxNumBuffer": 2000
  "narrowCamera.reverseX": true
  "narrowCamera.reverseY": true
  "narrowCamera.right.ROI.height": 1544
  "narrowCamera.right.ROI.offsetX": 8
  "narrowCamera.right.ROI.offsetY": 4
  "narrowCamera.right.ROI.width": 2064
  "narrowCamera.right.gain": 25
  {
    "framerate": 10.0,
    "numImages": 1,
    "type": "Manual",
    "maxEvents" : 100
  }
```