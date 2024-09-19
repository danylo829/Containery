document.addEventListener('DOMContentLoaded', () => {
    // const xterm = new Terminal();
    const xterm = new Terminal();
    const container = document.getElementById('terminal-container');
    xterm.open(container);
    const socket = io();

    xterm.resize(150, 45);

    socket.emit('start_session', {
        container_id: container_id
    });

    xterm.onData(e => {
        socket.emit('input', {
            command: e
        });
    });

    socket.on('output', function(data) {
        const output = data.data;
        xterm.write(output);
    });
});
