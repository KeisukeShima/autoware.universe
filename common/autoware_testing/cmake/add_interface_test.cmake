# Copyright 2022 The Autoware Foundation
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

# Add a interface test
# :param package_name: name of the package to interface test
# :type package_name: string
# :param package_exec: package executable to run during interface test
# :type executable_name: string
# :param PARAM_FILENAME: yaml filename containing test parameters
# :type PARAM_FILENAME: string
# :param EXECUTABLE_ARGUMENTS: arguments passed to tested executable
# :type EXECUTABLE_ARGUMENTS: string
# :param TOPIC_FILENAME: yaml filename containing topic types
# :type TOPIC_FILENAME: string

function(add_interface_test package_name executable_name)
  cmake_parse_arguments(PARSE_ARGV 2 interface_test "" "PARAM_FILENAME;EXECUTABLE_ARGUMENTS;TOPIC_FILENAME" "")

  set(ARGUMENTS "arg_package:=${package_name}" "arg_package_exe:=${executable_name}")

  if(interface_test_PARAM_FILENAME)
    list(APPEND ARGUMENTS "arg_param_filename:=${interface_test_PARAM_FILENAME}")
  endif()

  if(interface_test_EXECUTABLE_ARGUMENTS)
    list(APPEND ARGUMENTS "arg_executable_arguments:=${interface_test_EXECUTABLE_ARGUMENTS}")
  endif()

  if(interface_test_TOPIC_FILENAME)
    list(APPEND ARGUMENTS "arg_topic_filename:=${interface_test_TOPIC_FILENAME}")
  else()
    message(FATAL_ERROR "Can't find topic file for inteface test")
  endif()

  add_ros_test(
    ${autoware_testing_DIR}/../autoware_testing/interface_test.py
    TARGET "${executable_name}_interface_test"
    ARGS "${ARGUMENTS}"
    TIMEOUT "30"
  )
endfunction()
