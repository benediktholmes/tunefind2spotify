# Changelog

### 0.0.1 (prototype)
- first version of scraping, Spotify interface and database (shows only)

### 0.0.2
- added: scraping of all media types (show, movie, game)
- added: playlist description: (tunefind-url | last-updated: YYY-MM-DD HH:MM:SS)
- updated: documentation

### 0.1.0
- added: log module
- added: exceptions module
- added: logging in existing modules
- added: verbose information (loading bars)
- updated: corrected / specified exceptions being raised
- updated: refactoring of database module
- updated: broke down complex functions in scraper module

### 0.1.1
- added: unittests
- added: configs for linter and coverage

### 0.2.0
- added: requirements and config to build Sphinx docs
- added: automation of: lint & tests & doc build
- updated: store readable name of media (breaks old media table scheme)
- updated: playlist name and description at creation
- updated: minor fixes and attend to other open TODOs

### 1.0.0 (first stable version)
- added: LICENSE.md
- updated: Switched to use of setuptools instead of requirements files
- updated: use of tox 
- refactor: Grouped project modules in subpackages
- refactor: Split into api, main and actions modules
- refactor: Spotify API credentials not mandatory anymore for scraping
- refactor: API function names
- fixed: handling of missing & non-resolving Spotify links during fetching
- fixed: credentials argument not correctly parse in action class
