from setuptools import setup, find_namespace_packages


setup(
    name='clean_folder',
    version='0.1',
    description='folder parsing script',
    url='https://github.com/c-h-a-t-o-n/GOIT7',
    author='Zlata Sydorak',
    author_email='deklernesmerlen@gmail.com',
    license='MIT License (X11 License)',
    packages=find_namespace_packages(), 
    entry_points={
        'console_scripts': [
            'clean-folder=clean_folder.clean:main',
        ],
    },
)