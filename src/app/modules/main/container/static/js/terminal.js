document.addEventListener('DOMContentLoaded', () => {
    const contenBox = document.querySelector('.content-box.small');
    const form = document.getElementById('start-form');
    const terminalWrapper = document.getElementById('terminal-wrapper');
    const container = document.getElementById('terminal-container');
    const xterm = new Terminal();
    const commandSelect = document.getElementById('command-select');
    const commandInput = document.getElementById('command-input');
    const submitBtn = document.getElementById('submit-btn');
    let socket;

    xterm.open(container);

    // Disable select when there is any input in custom command
    commandInput.addEventListener('input', function () {
        if (commandInput.value.length > 0) {
            commandSelect.disabled = true;
        } else {
            commandSelect.disabled = false;
        }
    });

    form.addEventListener('submit', (event) => {
        
        window.onbeforeunload = function(e) {
            e.preventDefault();
        };

        event.preventDefault();  // Prevent the form from submitting the traditional way

        const user = document.getElementById('user').value;
        const containerId = submitBtn.getAttribute('data-container-id');

        // Use custom command if present, otherwise use selected command
        const command = commandInput.value.length > 0 ? commandInput.value : commandSelect.value;

        form.style.display = 'none';
        terminalWrapper.style.display = 'block';
        contenBox.classList.remove("small");

        socket = io();

        socket.emit('start_session', {
            container_id: containerId,
            user: user,
            command: command
        });

        xterm.resize(150, 44);

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
});
