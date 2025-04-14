# Sucolo Database Services

A Python package providing database services for the Sucolo project, including Elasticsearch and Redis clients with additional utilities for data processing and analysis.

## Features

- Elasticsearch client integration
- Redis client integration
- Data processing utilities
- H3 geospatial indexing support
- Type-safe data handling with Pydantic

## Requirements

- Python 3.11
- Poetry for dependency management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sucolo-database_services.git
cd sucolo-database_services
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up your environment variables in `.env` file:
```
# Example .env configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Development

### Code Style

This project uses several tools to maintain code quality:

- Black for code formatting
- Flake8 for linting
- MyPy for type checking
- isort for import sorting

Run the following command to format and check the code:
```bash
make format
```

### Testing

Run tests using pytest:
```bash
make test
```

## Project Structure

```
sucolo_database_services/
├── elasticsearch_client/  # Elasticsearch client implementation
├── redis_client/         # Redis client implementation
├── utils/                # Utility functions and helpers
├── tests/                # Test suite
└── db_service.py         # Main database service implementation
```

## Dependencies

Main dependencies:
- elasticsearch
- redis
- pandas
- geopandas
- h3
- pydantic
- python-dotenv

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
