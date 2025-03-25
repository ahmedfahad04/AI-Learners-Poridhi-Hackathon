# Poridhi AI Hackathon - Airflow Project

## Prerequisites

- Docker
- Docker Compose
- Git

## Project Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/poridhi-ai-hackathon.git
cd poridhi-ai-hackathon
```

2. Create necessary directories

```bash
mkdir -p ./dags ./logs ./plugins ./config
```

3. Set up environment variables

```bash
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```

## Docker Configuration

Fetch the docker compose file using this command:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.4/docker-compose.yaml'
```

## Running the Project

1. Start the Airflow services

```bash
docker-compose up -d
```

2. Check the status of the containers

```bash
docker-compose ps
```

3. Access the Airflow web interface

- Open your browser and navigate to `http://localhost:8080`
- Login with default credentials:
  - Username: `airflow`
  - Password: `airflow`

## Adding DAGs

Place your DAG files in the `./dags` directory. They will be automatically picked up by Airflow.

## Stopping the Project

```bash
docker-compose down
```

To clean up volumes as well:

```bash
docker-compose down -v
```

## Project Structure

```
poridhi-ai-hackathon/
├── dags/              # Your DAG files
├── logs/             # Airflow logs
├── plugins/          # Custom plugins
├── config/           # Configuration files
├── docker-compose.yaml
├── .env
└── README.md
```

## Troubleshooting

If you encounter permission issues:

```bash
sudo chown -R $(id -u):$(id -g) ./dags ./logs ./plugins ./config
```

To view logs:

```bash
docker-compose logs -f
```

## Notes

- The default Airflow version is 2.7.1. Update the image tag in docker-compose.yaml if you need a different version.
- Ensure ports 8080, 5432 (PostgreSQL), and 6379 (Redis) are available on your system.
- The project uses CeleryExecutor for distributed task execution.

## License

[Add your license information here]

## Contributors

[Add contributor information here]
