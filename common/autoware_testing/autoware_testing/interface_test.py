# Copyright 2022 the Autoware Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration

import rclpy
import yaml

from launch_ros.actions import Node
import launch_testing

import os
import pytest
import unittest
import shlex


def resolve_node(context, *args, **kwargs):
    interface_test_node = Node(
        package=LaunchConfiguration('arg_package'),
        executable=LaunchConfiguration('arg_package_exe'),
        namespace='test',
        parameters=[
            os.path.join(
                get_package_share_directory(LaunchConfiguration('arg_package').perform(context)),
                "param",
                LaunchConfiguration('arg_param_filename').perform(context)
            )
        ],
        arguments=shlex.split(LaunchConfiguration('arg_executable_arguments').perform(context))
    )
    return [interface_test_node]


@pytest.mark.launch_test
def generate_test_description():

    arg_package = DeclareLaunchArgument(
        'arg_package',
        default_value=['default'],
        description='Package containing tested executable'
    )
    arg_package_exe = DeclareLaunchArgument(
        'arg_package_exe',
        default_value=['default'],
        description='Tested executable'
    )
    arg_param_filename = DeclareLaunchArgument(
        'arg_param_filename',
        default_value=['test.param.yaml'],
        description='Test param file'
    )
    arg_executable_arguments = DeclareLaunchArgument(
        'arg_executable_arguments',
        default_value=[''],
        description='Tested executable arguments'
    )

    return LaunchDescription([
        arg_package,
        arg_package_exe,
        arg_param_filename,
        arg_executable_arguments,
        OpaqueFunction(function=resolve_node),
        launch_testing.actions.ReadyToTest()]
    )


class TestInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the ROS context for the test node
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        # Shutdown the ROS context
        rclpy.shutdown()

    def setUp(self):
        # Create a ROS node for tests
        self.test_node = rclpy.create_node("test_node")

    def tearDown(self):
        self.test_node.destroy_node()

    @staticmethod
    def get_topic(search_topic_type, topic_info):
        for (topic_name, topic_types, pub_count, sub_count) in topic_info:
            if search_topic_type == topic_types:
                return (topic_name, topic_types, pub_count, sub_count)
        return None

    def test_inputs_outputs(self, test_args):
        # Read topic configuration
        topic_file_path = os.path.join(
            get_package_share_directory(test_args['arg_package']),
            "param",
            test_args['arg_topic_filename'])
        with open(topic_file_path, 'r') as topic_file:
            loaded_topics = yaml.safe_load(topic_file)

        # Prepare topic info
        topic_names_and_types = self.test_node.get_topic_names_and_types()
        self.test_node.get_logger().info(f"Found topics: {topic_names_and_types}")
        topic_info = []
        for (topic_name, topic_types) in topic_names_and_types:
            pub_count = self.test_node.count_publishers(topic_name)
            sub_count = self.test_node.count_subscribers(topic_name)
            topic_info.append((topic_name, topic_types[0], pub_count, sub_count))

        # Check inputs and outputs
        for input_topic in loaded_topics['input_topics']:
            found_input_topic = self.get_topic(input_topic, topic_info)
            self.assertIsNotNone(
                found_input_topic,
                msg=f"[{test_args['arg_package']}:{test_args['arg_package_exe']}]: Could not find input topic '{input_topic}'")
            self.assertGreater(
                found_input_topic[3], 0,
                msg=f"[{test_args['arg_package']}:{test_args['arg_package_exe']}]: No subscribers for input topic '{input_topic}'")

        for output_topic in loaded_topics['output_topics']:
            found_output_topic = self.get_topic(output_topic, topic_info)
            self.assertIsNotNone(
                found_output_topic,
                msg=f"[{test_args['arg_package']}:{test_args['arg_package_exe']}]: Could not find output topic '{input_topic}'")
            self.assertGreater(
                found_output_topic[2], 0,
                msg=f"[{test_args['arg_package']}:{test_args['arg_package_exe']}]: No publishers for output topic '{input_topic}'")
