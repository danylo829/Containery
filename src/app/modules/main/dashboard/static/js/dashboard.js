document.addEventListener('DOMContentLoaded', function() {
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }
});

let updateInterval;

function updateUsage() {
    fetch('/dashboard/usage')
        .then(response => response.json())
        .then(data => {
            // Update CPU usage
            document.querySelector('.cpu-usage .progress').style.width = data.cpu + '%';
            document.querySelector('.cpu-usage .usage-text').innerText = `${data.cpu}%`;

            // Update RAM usage
            document.querySelector('.ram-usage .progress').style.width = data.ram_percent + '%';
            document.querySelector('.ram-usage .usage-text').innerText = `${data.ram_absolute} GB / ${data.ram_total} GB`;

            // Update Load Average
            const loadAverageCells = document.querySelectorAll('.load-average td');
            loadAverageCells[0].innerText = data.load_average[0].toFixed(2);
            loadAverageCells[1].innerText = data.load_average[1].toFixed(2);
            loadAverageCells[2].innerText = data.load_average[2].toFixed(2);
        })
        .catch(error => console.error('Error fetching usage data:', error));
}

function startUpdating() {
    updateInterval = setInterval(updateUsage, intervalSeconds * 1000);
    updateUsage();
}

function stopUpdating() {
    clearInterval(updateInterval);
}

document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopUpdating();
    } else {
        startUpdating();
    }
});

startUpdating();