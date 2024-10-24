import json
import socket
import select
import requests_unixsocket
from app.models import GlobalSettings

class Docker:
    def __init__(self):
        self.clients = {}  # Store client connections

    # GENERAL

    def perform_request(self, path, method='GET', payload=None):
        encoded_socket_path = GlobalSettings.get_setting("docker_socket").replace('/', '%2F')
        url = f'http+unix://{encoded_socket_path}{path}'
        session = requests_unixsocket.Session()
        try:
            if method == 'GET':
                response = session.get(url)
            if method == 'DELETE':
                response = session.delete(url)
            elif method == 'POST':
                response = session.post(url, json=payload)

            return response, response.status_code

        except Exception as e:
            return str(e), 500
    
    # EXEC

    def create_exec(self, endpoint, payload):
        """Create an exec instance and return its ID."""
        response, status_code = self.perform_request(endpoint, method='POST', payload=payload)
        if status_code in range(200, 300):
            exec_instance_json = response.json()
            return exec_instance_json.get("Id")
        return None

    def start_exec_session(self, exec_id, sid, socketio, docker_socket, timeout=3600, console_size=[44, 150]):
        exec_start_endpoint = f"/exec/{exec_id}/start"
        start_payload = {"Detach": False, "Tty": True, "ConsoleSize": console_size}

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(docker_socket)

        # Perform request to start the exec session
        # Construct the request manually
        request_line = f"POST {exec_start_endpoint} HTTP/1.1\r\n"
        request_body = json.dumps(start_payload)  # Ensure proper JSON encoding
        headers = f"Host: docker\r\nContent-Type: application/json\r\nContent-Length: {len(request_body)}\r\n"
        empty_line = "\r\n"

        request = request_line + headers + empty_line + request_body

        # Send the request through the client, ensuring it's encoded to bytes
        client.send(request.encode('utf-8'))

        # Store client for the session
        self.clients[sid] = client

        received_first_response = False
        timeout_counter = 0  # Keep track of no data periods
        while True:
            read_ready, _, _ = select.select([client], [], [], 1.0)  # Wait for 1 second
            if client in read_ready:
                output = client.recv(4096)
                if not output:
                    socketio.emit('output', {'data': '\nConnection closed by Docker.\r\n'}, to=sid)
                    break

                # Remove headers from output at first response
                if not received_first_response:
                    raw_data = output.decode('utf-8', errors='ignore')
                    header_end = raw_data.find("\r\n\r\n")
                    if header_end != -1:
                        output = raw_data[header_end + 4:]
                        received_first_response = True
                    else:
                        continue

                if not isinstance(output, str):
                    output = output.decode('utf-8')

                socketio.emit('output', {'data': output}, to=sid)
                socketio.sleep(0.1)
                timeout_counter = 0 
            else:
                timeout_counter += 1
                if timeout_counter > timeout:
                    client.send('\u0003'.encode('utf-8'))   # Send CTRL-C in case there is process running
                    socketio.sleep(3)                       # Allow time for the process to respond in case there is process running
                    client.send('\u0004'.encode('utf-8'))   # Send CTRL-D
                    socketio.emit('output', {'data': '\r\nSession timeout due to inactivity.\r\n'}, to=sid)

        # Close the session
        client.shutdown(socket.SHUT_WR)
        client.close()
        del self.clients[sid]

    def handle_command(self, command, sid):
        client = self.clients.get(sid)
        if client:
            client.send(command.encode('utf-8'))
        else:
            return 'No active session found.\r\n'
    
    # SYSTEM

    def info(self):
        return self.perform_request('/info')

    # CONTAINER

    def get_containers(self):
        return self.perform_request('/containers/json?all=true')

    def inspect_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/json')

    def get_processes(self, container_id):
        return self.perform_request(f'/containers/{container_id}/top')

    def get_logs(self, container_id, stdout=True, stderr=True):
        path = f'/containers/{container_id}/logs?stdout={str(stdout).lower()}&stderr={str(stderr).lower()}'
        response, status_code = self.perform_request(path)
        messages = []
        offset = 0

        if status_code not in range(200, 300):
            return response, status_code

        data = response.content

        while offset < len(data):
            stream_type = data[offset]

            if stream_type == 1:
                message_type = 'stdout'
            elif stream_type == 2:
                message_type = 'stderr'
            else:
                message_type = 'unknown'

            length_bytes = data[offset + 4:offset + 8]
            message_length = (length_bytes[0] << 24) + (length_bytes[1] << 16) + (length_bytes[2] << 8) + length_bytes[3]

            message_start = offset + 8
            message_end = message_start + message_length
            message_bytes = data[message_start:message_end].decode('utf-8', errors='ignore')

            messages.append({
                'type': message_type,
                'message': message_bytes
            })

            offset = message_end

        return messages, 200

    def restart_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/restart', method='POST')

    def start_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/start', method='POST')

    def stop_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}/stop', method='POST')

    def delete_container(self, container_id):
        return self.perform_request(f'/containers/{container_id}', method='DELETE')

    # IMAGE

    def get_images(self):
        return self.perform_request('/images/json')

    def inspect_image(self, image_id):
        return self.perform_request(f'/images/{image_id}/json')

    def delete_image(self, image_id):
        return self.perform_request(f'/images/{image_id}', method='DELETE')

    # VOLUME

    def get_volumes(self):
        return self.perform_request('/volumes')

    # NETWORK

    def get_networks(self):
        return self.perform_request('/networks')

    def inspect_network(self, network_id):
        return self.perform_request(f'/networks/{network_id}')

    def delete_network(self, image_id):
        return self.perform_request(f'/networks/{image_id}', method='DELETE')

