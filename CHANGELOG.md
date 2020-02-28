# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [x.x.x] - xxxx-xx-xx
### Added
- Approval mechanism. For some validators before changes would be applied to asset 
    they need to be approved through asset history admin page.

## [2.3.0] - 2020-01-14

### Added

- Add automatic task scheduling (JASSETS-120)
- Add CMC volume 24h getter (JASSETS-121)

### Changed

- Do not disable invalid assets (JASSETS-119)
- Convert static gas amount validator to getter (JASSETS-110)

### Fixed

- Better validator error handling and auto-restore
