import cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose
from cv_bridge import CvBridge
from ultralytics import YOLO


class YoloDetectorNode(Node):
    """Subscribes to a camera image topic, runs YOLO detection, and publishes
    vision_msgs/Detection2DArray plus an annotated image for visualization."""

    def __init__(self):
        super().__init__('yolo_detector_node')

        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('image_topic', 'camera/image_raw')

        model_path = self.get_parameter('model_path').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        image_topic = self.get_parameter('image_topic').value

        self.get_logger().info(f'Loading YOLO model: {model_path}')
        self.model = YOLO(model_path)
        self.bridge = CvBridge()

        # Camera stream is best-effort/high-rate; detections feed downstream
        # planning so they're published reliable, matching the JD's QoS-tuning ask.
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        detections_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.subscription = self.create_subscription(
            Image, image_topic, self.image_callback, sensor_qos)
        self.detections_pub = self.create_publisher(
            Detection2DArray, 'perception/detections', detections_qos)
        self.annotated_pub = self.create_publisher(
            Image, 'perception/image_annotated', sensor_qos)

    def image_callback(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)[0]

        detection_array = Detection2DArray()
        detection_array.header = msg.header

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_id = int(box.cls[0])
            score = float(box.conf[0])
            class_name = self.model.names[class_id]

            detection = Detection2D()
            detection.header = msg.header
            detection.bbox.center.position.x = (x1 + x2) / 2.0
            detection.bbox.center.position.y = (y1 + y2) / 2.0
            detection.bbox.size_x = x2 - x1
            detection.bbox.size_y = y2 - y1

            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hypothesis.class_id = class_name
            hypothesis.hypothesis.score = score
            detection.results.append(hypothesis)

            detection_array.detections.append(detection)

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f'{class_name} {score:.2f}', (int(x1), int(y1) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        self.detections_pub.publish(detection_array)

        # Built manually instead of via cv_bridge.cv2_to_imgmsg: that call's
        # cvtype_to_name lookup raises KeyError under some cv_bridge/NumPy
        # combinations even for plain bgr8 arrays.
        annotated_msg = Image()
        annotated_msg.header = msg.header
        annotated_msg.height = frame.shape[0]
        annotated_msg.width = frame.shape[1]
        annotated_msg.encoding = 'bgr8'
        annotated_msg.is_bigendian = 0
        annotated_msg.step = frame.shape[1] * 3
        annotated_msg.data = frame.tobytes()
        self.annotated_pub.publish(annotated_msg)


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
