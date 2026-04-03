from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="robot_inspector",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.28.0",
        "pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "pyyaml>=6.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        'ros2': [
            'rclpy>=0.10.0',
            'sensor-msgs>=0.0.5',
            'cv-bridge>=0.5.0',
            'image-transport>=0.1.0',
            'std-msgs>=0.0.5',
        ],
    },
    python_requires=">=3.8",
    author="Physical AI Lab",
    description="ROS2 package for intelligent robot inspection using Claude AI and AWS Bedrock",
    long_description="Smart robot inspector that combines ROS2 simulation, computer vision, and Claude AI for industrial inspection tasks",
    entry_points={
        'console_scripts': [
            'inspector_node=robot_inspector.ros_node:main',
            'run_inspector=robot_inspector.scripts.run_ros_node:main',
        ],
    },
    data_files=[
        ('share/robot_inspector/launch', ['launch/inspector.launch.py']),
        ('share/robot_inspector/config', ['config/inspector_config.yaml']),
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
