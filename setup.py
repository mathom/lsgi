import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = readme_file.read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    requirements = f.readlines()

setup(
    name='lsgi',
    version='0.0.1',
    packages=['lsgi'],
    install_requires=requirements,
    license='MIT License',
    description='Simple AWS Lambda WSGI adapter with a focus on AWS SAM support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mathom/lsgi',
    author='Matt Thompson',
)
