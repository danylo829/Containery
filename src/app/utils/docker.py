import json
import requests_unixsocket

import socket
import select

from app.models import GlobalSettings

clients = {}  # Dictionary to store client connections

class Docker:
    def __init__(self):
        self.socket_path = GlobalSettings.get_setting("docker_socket")
        self.encoded_socket_path = self.socket_path.replace('/', '%2F')

    def perform_request(self, path, method='GET'):
        url = f'http+unix://{self.encoded_socket_path}{path}'
        session = requests_unixsocket.Session()
        try:
            if method == 'GET':
                response = session.get(url)
            if method == 'POST':
                response = session.post(url)

            return response, response.status_code

        except Exception as e:
            return str(e), 500
    
    @staticmethod
    def info():
        return Docker().perform_request('/info')

    # **************** Container ****************
    
    @staticmethod
    def get_containers():
        return Docker().perform_request('/containers/json?all=true')

    @staticmethod
    def inspect_container(id):
        return Docker().perform_request(f'/containers/{id}/json')

    @staticmethod
    def get_processes(id):
        return Docker().perform_request(f'/containers/{id}/top')

    @staticmethod
    def get_logs(id, stdout=True, stderr=True):
        path = f'/containers/{id}/logs?stdout={str(stdout).lower()}&stderr={str(stderr).lower()}'
        response, status_code = Docker().perform_request(path)
        messages = []
        offset = 0

        if status_code not in range(200, 300):
            return response, status_code

        data = response.content

        while offset < len(data):
            # Extract message stream type
            stream_type = data[offset]
            
            # Determine stream type
            if stream_type == 1:
                message_type = 'stdout'
            elif stream_type == 2:
                message_type = 'stderr'
            else:
                message_type = 'unknown'

            # Extract the length of the message
            length_bytes = data[offset + 4:offset + 8]
            message_length = (length_bytes[0] << 24) + (length_bytes[1] << 16) + (length_bytes[2] << 8) + length_bytes[3]

            # Extract the message based on the length
            message_start = offset + 8
            message_end = message_start + message_length
            message_bytes = data[message_start:message_end].decode('utf-8', errors='ignore')

            # Build the JSON structure
            messages.append({
                'type': message_type,
                'message': message_bytes
            })
            
            # Move the offset to the next message
            offset = message_end

        return messages, 200

    @staticmethod
    def restart_container(id):
        return Docker().perform_request(f'/containers/{id}/restart', method='POST')

    # **************** ********* ****************

    # ****************** Image ******************
    @staticmethod
    def get_images():
        return Docker().perform_request('/images/json')

    @staticmethod
    def inspect_image(id):
        return Docker().perform_request(f'/images/{id}/json')
    
    # ****************** ***** ******************

    @staticmethod
    def get_volumes():
        return Docker().perform_request('/volumes')

    @staticmethod
    def get_networks():
        return Docker().perform_request('/networks')

    # **************** Exec and Interactive Session ****************
    @staticmethod
    def _send_headers(method, endpoint, payload=None):
        headers = f"{method} {endpoint} HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\n"
        body = json.dumps(payload) if payload else ""
        headers += f"Content-Length: {len(body)}\r\n\r\n"
        return headers + body

    @staticmethod
    def perform_request_exec(endpoint, method="GET", payload=None):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(GlobalSettings.get_setting("docker_socket"))

        request = Docker._send_headers(method, endpoint, payload)
        client.send(request.encode('utf-8'))

        response = client.recv(4096).decode('utf-8')
        client.close()

        headers, body = response.split("\r\n\r\n", 1)
        return body

    @staticmethod
    def start_exec_session(exec_id, sid, socketio, app):
        with app.app_context():  # Push the app context manually
            exec_start_endpoint = f"/exec/{exec_id}/start"
            start_payload = {"Detach": False, "Tty": True, "ConsoleSize": [45, 150]}

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(GlobalSettings.get_setting("docker_socket"))

            request = Docker._send_headers("POST", exec_start_endpoint, start_payload)
            client.send(request.encode('utf-8'))

            clients[sid] = client

            received_first_response = False
            while True:
                read_ready, _, _ = select.select([client], [], [], 0.1)
                if client in read_ready:
                    output = client.recv(4096)
                    if not output:
                        socketio.emit('output', {'data': '\nConnection closed by Docker.'}, to=sid)
                        break

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

            client.close()
            del clients[sid]

    def handle_command(command, sid):
        client = clients.get(sid)
        if client:
            client.send(command.encode('utf-8'))
        else:
            return 'No active session found.\n'