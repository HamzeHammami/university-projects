import launch
import launch.actions
import launch.substitutions
import launch_ros.actions
def generate_launch_description():
 return launch.LaunchDescription([
 launch.actions.DeclareLaunchArgument(
 'tutorial_pkg',
 default_value=[launch.substitutions.EnvironmentVariable('USER'), '_'],
 description='turotial_pkg_node'),
 launch_ros.actions.Node(
 package='tutorial_pkg', executable='tutorial_pkg_node', output='screen',
 name=[launch.substitutions.LaunchConfiguration('tutorial_pkg'),
'tutorial_pkg_node']),
])
