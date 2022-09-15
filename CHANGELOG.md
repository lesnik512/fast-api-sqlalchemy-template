# Changelog

## [0.3.0] - 2022-09-15
### Changed
- upgrade dependencies
- introduce poetry, Taskfile

## [0.2.0] - 2021-12-30
### Changed
- upgrade dependencies
- change starlette.TestClient with httpx.AsyncClient
- return raw responses in views to avoid double parsing

## [0.1.0] - 2021-07-25
### Changed
- remove `Test` model, clean migrations
- upgrade dependencies
- add builders for filters and sorting
- increase length limit of lines to 120
