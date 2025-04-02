from setuptools import find_packages, setup

setup(
    name="deepbook",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "openai",
        "langchain",
        "pydantic",
    ],
    description="AI-powered children's storybook generator",
    author="DeepBook Team",
    author_email="info@deepbook.example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Artistic Software",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)
