from setuptools import setup, find_packages

setup(
    name="robot_inspector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.28.0",
        "pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "pyyaml>=6.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.8",
    author="Physical AI Lab",
    description="ROS2 package for intelligent robot inspection using Claude AI and AWS Bedrock",
    long_description="Smart robot inspector that combines ROS2 simulation, computer vision, and Claude AI for industrial inspection tasks",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
