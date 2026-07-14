from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    device_index_arg = DeclareLaunchArgument('device_index', default_value='0')
    model_path_arg = DeclareLaunchArgument('model_path', default_value='yolov8n.pt')
    confidence_arg = DeclareLaunchArgument('confidence_threshold', default_value='0.5')

    camera_node = Node(
        package='perception_pipeline',
        executable='camera_publisher_node',
        name='camera_publisher_node',
        parameters=[{'device_index': LaunchConfiguration('device_index')}],
        output='screen',
    )

    detector_node = Node(
        package='perception_pipeline',
        executable='yolo_detector_node',
        name='yolo_detector_node',
        parameters=[{
            'model_path': LaunchConfiguration('model_path'),
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
        }],
        output='screen',
    )

    return LaunchDescription([
        device_index_arg,
        model_path_arg,
        confidence_arg,
        camera_node,
        detector_node,
    ])
