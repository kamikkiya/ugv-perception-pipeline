# Project 1: Real-Time Multi-Sensor Perception & Edge Optimization Pipeline

Simulated UGV perception stack: object detection, terrain classification, LiDAR
point-cloud fusion, and edge-optimized inference — built for the Autonomous
Navigation and Perception Engineer role (ROS 2, YOLOv8, DeepLabV3+, Open3D, TensorRT).

Developed on Windows; built and run on Linux (ROS 2 Jazzy / Ubuntu 24.04) since
ROS 2 and Gazebo are Linux-native.

## Milestone 1 (current): Webcam object detection over ROS 2

Two nodes, no Gazebo/LiDAR required yet — proves the ROS 2 + YOLO pipeline works
end-to-end before adding simulation:

- `camera_publisher_node` — reads your webcam, publishes `sensor_msgs/Image` on
  `/camera/image_raw` (best-effort QoS, matches "QoS tuning for high-bandwidth
  streaming" in the JD).
- `yolo_detector_node` — subscribes to the camera topic, runs YOLOv8, publishes
  `vision_msgs/Detection2DArray` on `/perception/detections` (reliable QoS, since
  downstream planning needs guaranteed delivery) and an annotated preview image
  on `/perception/image_annotated`.

## Setup (on your Ubuntu 24.04 / ROS 2 Jazzy laptop)

```bash
# ROS 2 + vision deps
sudo apt update
sudo apt install -y ros-jazzy-vision-msgs ros-jazzy-cv-bridge ros-jazzy-rviz2 \
    python3-opencv python3-pip

# Python inference deps
pip install ultralytics
```

Copy/clone this repo onto the Linux machine, then build:

```bash
cd project/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
ros2 launch perception_pipeline perception.launch.py
```

Optional args: `device_index:=0 model_path:=yolov8n.pt confidence_threshold:=0.5`

Visualize either topic:

```bash
ros2 run rqt_image_view rqt_image_view /perception/image_annotated
# or inspect raw detections
ros2 topic echo /perception/detections
```

First run downloads `yolov8n.pt` automatically via `ultralytics`.

> Note: field names in `vision_msgs/Detection2D` differ across ROS 2 releases.
> If the detector node errors on message fields, run
> `ros2 interface show vision_msgs/msg/Detection2D` and adjust
> `yolo_detector_node.py` to match the installed version.

## Roadmap

1. Webcam + YOLOv8 over ROS 2 (this milestone)
2. Gazebo world with mixed terrain (grass/gravel/mud/potholes) + simulated LiDAR
3. DeepLabV3+ terrain segmentation (fine-tuned on RELLIS-3D/RUGD)
4. Open3D point-cloud clustering + 3D bounding-box fitting on simulated LiDAR
5. Camera-LiDAR calibration (TF from URDF + real webcam intrinsic calibration)
6. Fusion node combining YOLO boxes + LiDAR clusters into one `Detection2DArray`
7. Model optimization: ONNX export, TensorRT, INT8 quantization, latency/FPS benchmarks
8. `rosbag2` regression recordings, Foxglove/RViz2 visualization
