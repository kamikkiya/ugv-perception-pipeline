# Project 1: Real-Time Multi-Sensor Perception & Edge Optimization Pipeline

Simulated UGV perception stack: object detection, terrain classification, LiDAR
point-cloud fusion, and edge-optimized inference — built for the Autonomous
Navigation and Perception Engineer role (ROS 2, YOLOv8, DeepLabV3+, Open3D, TensorRT).

Developed on Windows; built and run on Linux (ROS 2 Jazzy / Ubuntu 24.04) since
ROS 2 and Gazebo are Linux-native.

## Milestone 1 (current): TurtleBot3 + YOLOv8 in Gazebo

Fully simulated — no real camera/webcam needed. TurtleBot3 Waffle's built-in
Gazebo camera plugin publishes `sensor_msgs/Image`, and our node consumes it
directly:

- `yolo_detector_node` — subscribes to the sim camera topic, runs YOLOv8,
  publishes `vision_msgs/Detection2DArray` on `/perception/detections`
  (reliable QoS, since downstream planning needs guaranteed delivery) and an
  annotated preview image on `/perception/image_annotated`.

The launch file spawns TurtleBot3 in Gazebo's stock `turtlebot3_world` and
starts the detector alongside it.

## Setup (on your Ubuntu 24.04 / ROS 2 Jazzy VM)

```bash
# ROS 2 + vision deps
sudo apt update
sudo apt install -y ros-jazzy-vision-msgs ros-jazzy-cv-bridge ros-jazzy-rviz2 \
    python3-opencv python3-pip

# Python inference deps
pip install --break-system-packages ultralytics

# TurtleBot3 simulation packages (try apt first)
sudo apt install -y ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-msgs ros-jazzy-turtlebot3-simulations
```

> If those `turtlebot3*` apt packages aren't available for Jazzy yet, build
> from source instead: clone `ROBOTIS-GIT/turtlebot3`,
> `ROBOTIS-GIT/turtlebot3_msgs`, and `ROBOTIS-GIT/turtlebot3_simulations`
> into `ros2_ws/src/`, check out the branch matching your ROS distro (see
> each repo's branch list / ROBOTIS e-manual), then `colcon build`.

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

This launches Gazebo with TurtleBot3 Waffle in `turtlebot3_world`, plus the
detector node. Optional args: `model_path:=yolov8n.pt confidence_threshold:=0.5
image_topic:=camera/image_raw`.

First, confirm the real camera topic name — TurtleBot3's exact topic can vary
by version:

```bash
ros2 topic list | grep -i camera
```

If it's not `/camera/image_raw`, pass the real one:
`ros2 launch perception_pipeline perception.launch.py image_topic:=<actual_topic>`

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

1. ~~TurtleBot3 + YOLOv8 in Gazebo (this milestone)~~
2. Custom Gazebo world with mixed terrain (grass/gravel/mud/potholes) + simulated LiDAR
3. DeepLabV3+ terrain segmentation (fine-tuned on RELLIS-3D/RUGD)
4. Open3D point-cloud clustering + 3D bounding-box fitting on simulated LiDAR
5. Camera-LiDAR calibration (static TF from URDF/SDF)
6. Fusion node combining YOLO boxes + LiDAR clusters into one `Detection2DArray`
7. Model optimization: ONNX export, TensorRT, INT8 quantization, latency/FPS benchmarks
8. `rosbag2` regression recordings, Foxglove/RViz2 visualization
