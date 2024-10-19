# Containery

## Overview
Containery is a container management web application that offers a powerful, fast, and lightweight interface to manage Docker containers. Whether you are an individual developer or managing a fleet of containers in production, Containery simplifies the process by providing an intuitive UI with essential container management capabilities.

## Features
- **Docker Management**: Manage containers, images, networks, and volumes within a unified interface.
- **Terminal and Logs**: View container logs and interact with container terminals directly in the UI.
- **Responsive Web Interface**: Access and manage Docker resources from any device.
- **User Management**: Authentication, user profiles, and roles. Ensure that each member has the right level of access to perform their tasks efficiently.

## Deployment

To deploy Containery, use the following `docker-compose.yml` configuration. Please note that the `docker-compose.yml` in the repository is set up for development purposes.

```yaml
services:
  app:
    image: containery:latest
    container_name: containery
    restart: "unless-stopped"
    ports:
      - "5000:5000"
    volumes:
      - containery_data:/app_data
      - /var/run/docker.sock:/var/run/docker.sock
    env_file:
      - ./.env

volumes:
  containery_data:
```

Once the application starts, you can access it by navigating to **[http://localhost:5000](http://localhost:5000)** in your browser.

### Environment Variables
Create a `.env` file next to `docker-compose.yml` with the following content:

```plaintext
SECRET_KEY=12345678
CSRF_SECRET_KEY=87654321
DEBUG=False
```

This `.env` file contains environment variables used by the application:
- **SECRET_KEY**: Used for session encryption and security.
- **CSRF_SECRET_KEY**: Used to secure against Cross-Site Request Forgery (CSRF).
- **DEBUG**: Set to `True` during development. Set to `False` in production to disable debugging.

Make sure to customize `SECRET_KEY` and `CSRF_SECRET_KEY` values.

### NGINX Reverse Proxy (Optional)
If you need to expose the application over a domain or HTTPS, you can use NGINX as a reverse proxy. Below is a sample NGINX configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://app:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

If you're using NGINX as a reverse proxy, remove the `ports` section from the `docker-compose.yml` file for the app service.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
