# ESewa Full-Stack Application

A full-stack application with a **Django** backend and **React** frontend, using **Docker**.

## Requirements

- **Docker**: [Download Docker](https://www.docker.com/get-started)

## Setup and Running the Application

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/esewa.git
    cd esewa
    ```

2. Build and start the application:

    ```bash
    docker-compose up --build
    ```

3. Access the application:

    - Backend (Django API): [http://localhost:8000](http://localhost:8000)
    - Frontend (Angular): [http://localhost:4200](http://localhost:4200)

## Stopping the Application

To stop the containers:

```bash
docker-compose down
