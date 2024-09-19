document.addEventListener('DOMContentLoaded', function() {
    spinner = document.querySelector('.loading-spinner');
    spinner.remove();
});

let updateInterval;

function updateUsage() {
    fetch('/dashboard/usage')
        .then(response => response.json())
        .then(data => {
            document.querySelector('.cpu-usage .progress').style.width = data.cpu + '%';
            document.querySelector('.cpu-usage .usage-text').innerText = `${data.cpu}%`;

            document.querySelector('.ram-usage .progress').style.width = data.ram_percent + '%';
            document.querySelector('.ram-usage .usage-text').innerText = `${data.ram_absolute}GB / ${data.ram_total}GB`;
        })
        .catch(error => console.error('Error fetching usage data:', error));
}

function startUpdating() {
    updateInterval = setInterval(updateUsage, 5000);
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