import json
import os
import sys
import unittest

from setuptools import setup, find_namespace_packages, Command
from setuptools.errors import DistutilsError

# PROJECT SPECIFIC VAR
PIPENV_PROJECT: bool = True  # True -> use Pipfile.lock for *install_requires*, False -> Use requirements.txt
PROJECT_NAME: str = 'hellopysdl'
VERSION: str = '1.0.0'
AUTHOR: str = 'author'
EMAIL: str = 'author@mail.com'
DESCRIPTION: str = 'A Python boilerplate inspired from the Maven Standard Directory Layout'
URL: str = f'https://github.com/St4rG00se/{PROJECT_NAME}'
LICENSE: str = 'MIT'
ENTRY_POINT: dict[str, list[str]] = {
    'console_scripts': [
        f'hello = {PROJECT_NAME}.__main__:hello'
    ]
}


# SETUP FUNCTIONS
def read_file(file_path: str) -> str:
    with open(file_path) as file:
        return file.read()


def get_deps_from_pipfile(section: str = "default", pipfile_path: str = "Pipfile.lock") -> list[str]:
    with open(pipfile_path) as pipfile:
        pipfile_content = json.load(pipfile)

    return [package + detail.get('version', "") for package, detail in pipfile_content.get(section, {}).items()]


def get_deps_from_requirements(requirements_path: str = "requirements.txt") -> list[str]:
    return read_file(requirements_path).splitlines()


def get_deps(use_pipfile: bool = True) -> list[str]:
    return get_deps_from_pipfile() if use_pipfile else get_deps_from_requirements()


def to_package_dir(folder_path: str, packages: list) -> dict[str, str]:
    return {pkg: f"{folder_path}/{pkg.replace('.', '/')}" for pkg in packages}


# FIXED VAR
MAIN_FOLDER: str = 'src/main'
SRC_FOLDER: str = f'{MAIN_FOLDER}/python'
RESOURCES_FOLDER: str = f'{MAIN_FOLDER}/resources'

TEST_FOLDER: str = 'src/test'
TEST_SRC_FOLDER: str = f'{TEST_FOLDER}/python'
TEST_RESOURCES_FOLDER: str = f'{TEST_FOLDER}/resources'
TEST_FILE_PATTERN: str = "*[Tt]est*.py"

# Configure sys.path for command execution
PROJECT_PATH: str = os.path.dirname(__file__)
sys.path.append(os.path.join(PROJECT_PATH, SRC_FOLDER))
sys.path.append(os.path.join(PROJECT_PATH, RESOURCES_FOLDER))
sys.path.append(os.path.join(PROJECT_PATH, TEST_SRC_FOLDER))
sys.path.append(os.path.join(PROJECT_PATH, TEST_RESOURCES_FOLDER))

SRC_PACKAGES: list = find_namespace_packages(where=SRC_FOLDER)
RESOURCES_PACKAGES: list = list(
    filter(lambda pkg: pkg not in SRC_PACKAGES, find_namespace_packages(where=RESOURCES_FOLDER))
)
PACKAGES: list = SRC_PACKAGES + RESOURCES_PACKAGES

# {'': SRC_FOLDER} workaround for pip install -e but resources will not work
# see: https://github.com/pypa/setuptools/issues/230
SRC_PACKAGES_DIR: dict = {'': SRC_FOLDER}
RESOURCES_PACKAGES_DIR: dict = to_package_dir(RESOURCES_FOLDER, RESOURCES_PACKAGES)
PACKAGES_DIR: dict = dict(RESOURCES_PACKAGES_DIR, **SRC_PACKAGES_DIR)


# SETUP COMMAND CLASSES
class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    # noinspection PyMethodMayBeStatic
    def run(self):
        # Prepare tests
        test_loader = unittest.defaultTestLoader
        test_suite = test_loader.discover(os.path.join(PROJECT_PATH, TEST_SRC_FOLDER), pattern=TEST_FILE_PATTERN)

        # Run tests
        test_result = unittest.TextTestRunner().run(test_suite)

        if not test_result.wasSuccessful():
            raise DistutilsError('Test failed: %s' % test_result)


# SETUP
setup(
    name=PROJECT_NAME,
    version=VERSION,
    author=AUTHOR,
    url=URL,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    license=LICENSE,
    packages=PACKAGES,
    package_dir=PACKAGES_DIR,
    package_data={'': ['*']},
    include_package_data=True,
    install_requires=get_deps(PIPENV_PROJECT),
    entry_points=ENTRY_POINT,
    cmdclass={'test': TestCommand}
)
