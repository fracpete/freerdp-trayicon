from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="freerdp_trayicon",
    description="Python library that adds a tray icon for easily launching freerdp connections.",
    long_description=(
        _read('DESCRIPTION.rst') + b'\n' +
        _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/fracpete/freerdp-trayicon",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Desktop Environment',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
    ],
    license='Apache 2.0',
    package_dir={
        '': 'src'
    },
    packages=[
        "freerdp_tray",
    ],
    include_package_data=True,
    version="0.0.1",
    author='Peter "fracpete" Reutemann',
    author_email='fracpete@gmail.com',
    install_requires=[
        "pycairo",
        "PyGObject",
    ],
    data_files=[
        ('share/applications/', ['share/applications/freerdp-tray.desktop']),
        ('share/icons/', ['share/icons/freerdp-tray.png']),
    ],
    entry_points={
        "console_scripts": [
            "freerdp-tray=freerdp_tray.tray:sys_main",
        ]
    }
)
