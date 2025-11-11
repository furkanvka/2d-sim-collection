cmake_minimum_required(VERSION 3.10)
project(n-body-problem-in-c++)

# Use C++17 or later
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find SFML package (graphics, window, system modules)
find_package(SFML 2.5 COMPONENTS graphics window system REQUIRED)

# Add your source files
add_executable(${PROJECT_NAME} main.cpp)

# Link SFML libraries
target_link_libraries(${PROJECT_NAME} sfml-graphics sfml-window sfml-system)
