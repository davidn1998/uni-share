from setuptools import find_packages, setup

setup(
    name='unishare',
    version='1.0.0',
    license='MIT',
    description='A app for university students to share resources.',
    author='David Nwachukwu',
    author_email='davidnw1998@gmail.com',
    packages=find_packages(),
    include_pacakge_data=True,
    url='https://github.com/davidn1998/uni-share',
    keywords = ['UNISHARE', 'UNIVERSITY', 'STUDENTS', 'WEBSITE', 'APP'],
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'psycopg2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Framework :: Flask',
        'Programming Language :: Python :: 3', 
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
  ],
)