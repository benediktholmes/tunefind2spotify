from setuptools import setup, find_packages

setup(
    name='tunefind2spotify',
    version=open('VERSION', 'r').readline(),
    description='Create Spotify playlists for your favorite movies, shows and games with data gathered on Tunefind.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='Benedikt Holmes',
    author_email='20526499+benediktholmes@users.noreply.github.com',
    url='https://benediktholmes.github.io/tunefind2spotify',
    packages=find_packages(include=['tunefind2spotify', 'tunefind2spotify.*']),
    install_requires=[
        'argparse>=1.1',
        'requests>=2.27.1',
        'spotipy>=2.20.0',
        'tqdm>=4.64.1'
    ],
    extras_require={'dev':
                    ['coverage>=6.4.4',
                     'flake8>=3.9.1',
                     'pytest>=7.1.3'
                     ],
                    'doc':
                    ['myst-parser>=0.18.1',
                     'sphinx>=5.2.1',
                     'sphinx-rtd-theme==1.0.0'
                     ]
                    },
    entry_points={
        'console_scripts': ['tunefind2spotify=tunefind2spotify.cmd.main:entrypoint']
    },
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        # 'Operating System :: OS Independent'
    ]
    # package_data={'tunefind2spotify': ['data/schema.json']}
)
