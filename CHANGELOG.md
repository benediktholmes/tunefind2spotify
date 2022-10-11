# Changelog

### 0.0.1
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
- fixed: handling of missing Spotify links during scraping

### 0.1.1
- added: unittests
- added: configs for linter and coverage

### 0.2.0
- added: requirements and config to build Sphinx docs
- added: automation of: lint & tests & doc build
- update: store readable name of media (breaks old media table scheme)
- update: playlist name and description at creation
- update: minor fixes and attend to other open TODOs
