#python setup file for the kiwi package
from setuptools import setup, find_packages

setup(
    name='kiwi',
    version='0.1.0',
    description='A Common reusable BDD test automation framework in python',
    author='zaidongl',
    long_description=open("../README.md", encoding="utf-8").read(), # 详细描述
    long_description_content_type="text/markdown", # 描述内容的格式
    packages=find_packages(), # 自动查找子模块

    install_requires=[
        'behave==1.3.3',
        'certifi==2025.8.3',
        'charset-normalizer==3.4.3',
        'colorama==0.4.6',
        'cucumber-expressions==18.0.1',
        'cucumber-tag-expressions==6.2.0',
        'greenlet==3.2.4',
        'idna==3.10',
        'iniconfig==2.1.0',
        'packaging==25.0',
        'parse==1.20.2',
        'parse_type==0.6.6',
        'playwright==1.55.0',
        'pluggy==1.6.0',
        'pyee==13.0.0',
        'Pygments==2.19.2',
        'pytest==8.4.2',
        'pytest-base-url==2.1.0',
        'pytest-playwright==0.7.1',
        'python-slugify==8.0.4',
        'PyYAML==6.0.2',
        'requests==2.32.5',
        'six==1.17.0',
        'text-unidecode==1.3',
        'typing_extensions==4.15.0',
        'urllib3==2.5.0'
    ], # 依赖包]
    # entry_points={"console_scripts": ["kiwi=example.module:main"]}, # 命令行入口
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    python_requires=">=3.11" # Python 版本要求
)