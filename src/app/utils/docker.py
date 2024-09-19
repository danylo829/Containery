import json
import pycurl
from io import BytesIO
import time
import struct, io

import socket
import select

from app.models import GlobalSettings

clients = {}  # Dictionary to store client connections

class Docker:
    @staticmethod
    def perform_request(endpoint, method='GET', data=None):
        docker_url = f'http://unix/{GlobalSettings.get_setting("docker_api_version")}{endpoint}'
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, docker_url)
        curl.setopt(curl.WRITEFUNCTION, buffer.write)
        curl.setopt(curl.UNIX_SOCKET_PATH, GlobalSettings.get_setting("docker_socket"))

        curl.setopt(curl.TIMEOUT, 100)  # total timeout in seconds
        curl.setopt(curl.CONNECTTIMEOUT, 5)  # connection timeout in seconds

        if method == 'POST':
            curl.setopt(curl.POST, 1)
        elif method == 'DELETE':
            curl.setopt(curl.CUSTOMREQUEST, 'DELETE')

        if data:
            curl.setopt(curl.POSTFIELDS, json.dumps(data))
            curl.setopt(curl.HTTPHEADER, ['Content-Type: application/json'])

        try:
            curl.perform()
            response_code = curl.getinfo(curl.RESPONSE_CODE)
            response_body = buffer.getvalue()

            try:
                response_text = response_body.decode('utf-8')
                return json.loads(response_text), response_code
            except (UnicodeDecodeError, json.JSONDecodeError):
                # If decoding fails, return raw response
                return response_body, response_code

        except Exception as e:
            return {'error': str(e)}, 500

        finally:
            curl.close()

    @staticmethod
    def info():
        return Docker.perform_request('/info')

    # **************** Container ****************
    
    @staticmethod
    def get_containers():
        return Docker.perform_request('/containers/json?all=true')

    @staticmethod
    def inspect_container(id):
        return Docker.perform_request(f'/containers/{id}/json')

    @staticmethod
    def get_processes(id):
        return Docker.perform_request(f'/containers/{id}/top')

    @staticmethod
    def get_logs(id, stdout=True, stderr=True):
        endpoint = f'/containers/{id}/logs?stdout={str(stdout).lower()}&stderr={str(stderr).lower()}'
        response_body, response_code = Docker.perform_request(endpoint)
        messages = []
        offset = 0

        data = response_body

        if not data:
            return 'No data', 500

        while offset < len(data):
            # Extract message stream type
            stream_type = data[offset]
            
            # Determine stream type
            if stream_type == 1:
                message_type = 'stdout'
            elif stream_type == 2:
                message_type = 'stderr'
            else:
                return 'Invalid stream type', 500

            # Extract the length of the message
            length_bytes = data[offset + 4:offset + 8]
            message_length = struct.unpack('>I', length_bytes)[0]

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
        return Docker.perform_request(f'/containers/{id}/restart', method='POST')

    # **************** ********* ****************

    # ****************** Image ******************
    @staticmethod
    def get_images():
        return Docker.perform_request('/images/json')

    @staticmethod
    def inspect_image(id):
        return Docker.perform_request(f'/images/{id}/json')
    
    # ****************** ***** ******************

    @staticmethod
    def get_volumes():
        return Docker.perform_request('/volumes')

    @staticmethod
    def get_networks():
        return Docker.perform_request('/networks')

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
            return 'No active session found.'