from setuptools import setup, find_packages

setup(
    name="magic-game",
    version="1.0.0",
    author="HAMIC",
    description="A 2D magic fighting game with AI gesture recognition",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],
    install_requires=[
        "pygame==2.6.1",
        "opencv-python==4.13.0.92",
        "mediapipe==0.10.14",
        "numpy>=1.24.0",
        "joblib==1.5.3",
        "scikit-learn==1.8.0",
        "pandas==3.0.1",
    ],
    entry_points={
        "console_scripts": [
            "magic-game=main:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.10",
)
