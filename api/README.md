# API

`idol-db` exposes canonical structured idol data to research and application repositories.

Initial contract:

- `GET /events`
- `GET /events/:id`
- `GET /idols`
- `GET /idols/:id`
- `GET /observations`
- `GET /observations/:id`

Implementation is intentionally left loosely coupled from the data model.
