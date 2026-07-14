import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    model_path_arg = DeclareLaunchArgument('model_path', default_value='yolov8n.pt')
    confidence_arg = DeclareLaunchArgument('confidence_threshold', default_value='0.5')
    image_topic_arg = DeclareLaunchArgument('image_topic', default_value='camera/image_raw')

    # TurtleBot3 Waffle includes a simulated camera; Burger does not.
    set_model_env = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle')

    turtlebot3_world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('turtlebot3_gazebo'),
                'launch',
                'turtlebot3_world.launch.py',
            )
        )
    )

    detector_node = Node(
        package='perception_pipeline',
        executable='yolo_detector_node',
        name='yolo_detector_node',
        parameters=[{
            'model_path': LaunchConfiguration('model_path'),
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
            'image_topic': LaunchConfiguration('image_topic'),
        }],
        output='screen',
    )

    return LaunchDescription([
        model_path_arg,
        confidence_arg,
        image_topic_arg,
        set_model_env,
        turtlebot3_world_launch,
        detector_node,
    ])
