document.getElementById('validation-form').addEventListener('submit', function(event) {
    event.preventDefault();

    let environment = document.getElementById('environment').value;

    fetch('/start_validation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ environment: environment })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('status').innerText = data.status;
        updateStatus();
    });
});

function updateStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('status').innerText = data.status;
            let results = data.results.map(result => `<p>${result[0]}</p>`).join('');
            document.getElementById('results').innerHTML = results;

            if (data.status === 'Running') {
                setTimeout(updateStatus, 2000); // Update every 2 seconds
            }
        });
}

updateStatus();
