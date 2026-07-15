import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    model_path_arg = DeclareLaunchArgument('model_path', default_value='yolov8n.pt')
    confidence_arg = DeclareLaunchArgument('confidence_threshold', default_value='0.5')
    image_topic_arg = DeclareLaunchArgument('image_topic', default_value='camera/image_raw')

    # TurtleBot3 Waffle includes a simulated camera; Burger does not.
    set_model_env = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle')

    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    launch_file_dir = os.path.join(turtlebot3_gazebo_dir, 'launch')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

    world = os.path.join(turtlebot3_gazebo_dir, 'worlds', 'turtlebot3_world.world')

    # Mirrors turtlebot3_gazebo/launch/turtlebot3_world.launch.py but omits its
    # gzclient_cmd (the GUI, `gz sim -g`) -- that hangs on this VM since there's
    # no GPU passthrough for its 3D rendering. Server + sensors run headless;
    # visualize via rqt_image_view/RViz2 instead of the Gazebo 3D viewport.
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r -s -v2 ', world], 'on_exit_shutdown': 'true'}.items()
    )

    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    spawn_turtlebot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'spawn_turtlebot3.launch.py')
        ),
        launch_arguments={'x_pose': x_pose, 'y_pose': y_pose}.items()
    )

    set_env_vars_resources = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(turtlebot3_gazebo_dir, 'models')
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
        set_env_vars_resources,
        gzserver_cmd,
        robot_state_publisher_cmd,
        spawn_turtlebot_cmd,
        detector_node,
    ])
