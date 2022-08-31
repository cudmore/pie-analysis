from setuptools import setup, find_packages

#includePackages = ['canvas', 'canvas.*', 'canvas.inter*face']
includePackages = ['videoapp']

setup(
    name='VideoAnnotate',
    version='0.1.0',
	description='',
	long_description='',
	author='Robert Cudmore',
	author_email='robert.cudmore@gmail.com',
	url='https://github.com/cudmore/pie-analysis',
    keywords=['behavior', 'ethology', 'video', 'annotate', 'mouse', 'transgenic', 'maternal'],
    
    packages=find_packages(include=includePackages, exclude=[]),

    install_requires=[
        'numpy',
        'opencv-python==4.5.3.56',
        'Pillow'
    ],
    # extras_require={
    #     # bioformats depends on python-javabridge which requires path to JDK/JRE
    #     'bioformats': ['python-bioformats'],
    # },

    entry_points={
        'console_scripts': [
            'videoannotate=videoapp.videoApp:main',
        ]
    },

)
