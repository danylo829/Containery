# Containery
![Version](https://img.shields.io/github/v/tag/danylo829/containery?label=version)
![License](https://img.shields.io/github/license/danylo829/containery)
![Image Size](https://img.shields.io/docker/image-size/danylo829/containery/latest)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Last Commit](https://img.shields.io/github/last-commit/danylo829/containery)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)

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
      - containery_data:/containery_data
      - containery_static:/containery/app/static/dist
      - /var/run/docker.sock:/var/run/docker.sock:ro

volumes:
  containery_data:
    name: containery_data
  containery_static:
    name: containery_static
```

Once the application starts, you can access it by navigating to **[http://localhost:5000](http://localhost:5000)** in your browser. Feel free to change host port (e.g. 80:5000, 8080:5000)

### NGINX Reverse Proxy (Optional)
If you need to expose the application over a domain, add HTTPS or improve page loads by caching static content, you can use NGINX as a reverse proxy. Below is a sample NGINX configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_vary on;
    gzip_min_length 1024;

    location ^~ /static/dist/ {
        root /var/www/containery;
        autoindex off;
        access_log off;
        expires max;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location /socket.io {
        proxy_pass http://app:5000/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";

        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://app:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Note**:  
1. If you're using NGINX as a reverse proxy, remove the `ports` section from the `docker-compose.yml` file for the `app` service.  
2. To enable static content caching, ensure that the `containery_static` volume is mounted to `/var/www/containery/static/dist` in the NGINX configuration. 
3. If you do not wish to enable static content caching, you can omit the `containery_static` volume mount and remove the `/static/dist/` location block from the NGINX configuration.

### Environment variables

#### Docker Configuration
- **`DOCKER_SOCKET_PATH`**: The path to the Docker socket. Defaults to `/var/run/docker.sock`. You can specify a custom path if the socket is located elsewhere.

#### Development
- **`SECRET_KEY`**: A secret key used for cryptographic operations. If not provided, a random 32-byte hexadecimal string will be generated.
- **`CSRF_SECRET_KEY`**: A secret key specifically for CSRF protection. If not provided, a random 32-byte hexadecimal string will be generated.
- **`SQLALCHEMY_DATABASE_URI`**: The database connection URI. Defaults to `sqlite:////containery_data/containery.db` for local development.
- **`SQLALCHEMY_TRACK_MODIFICATIONS`**: A flag to enable or disable SQLAlchemy's event system. Defaults to `False`.
- **`DEBUG`**: Enables or disables debug mode. Defaults to `False`.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
