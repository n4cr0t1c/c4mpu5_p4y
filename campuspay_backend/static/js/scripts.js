// Handle user registration
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const rfid_id = document.getElementById('rfid_id').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rfid_id, username, password }),
    });

    const result = await response.json();
    document.getElementById('register-message').innerText = result.message || result.error;
});

// Handle transactions
document.getElementById('transaction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const rfid_id = document.getElementById('transaction_rfid_id').value;
    const amount = document.getElementById('amount').value;

    const response = await fetch('/api/transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rfid_id, amount }),
    });

    const result = await response.json();
    document.getElementById('transaction-message').innerText = result.message || result.error;
});

// Handle transaction history retrieval
document.getElementById('history-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const rfid_id = document.getElementById('history_rfid_id').value;

    const response = await fetch(`/api/history?rfid_id=${rfid_id}`);
    const result = await response.json();

    if (result.history) {
        const historyDiv = document.getElementById('history-results');
        historyDiv.innerHTML = '<h3>Transaction History:</h3>';
        result.history.forEach((transaction) => {
            historyDiv.innerHTML += `<p>${transaction.timestamp}: $${transaction.amount}</p>`;
        });
    } else {
        document.getElementById('history-results').innerText = result.error;
    }
});

let isAuthenticating = false;
let intervalId = null;

function authenticateFace() {
    if (isAuthenticating) return; // Prevent multiple simultaneous requests
    isAuthenticating = true;

    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob, 'capture.jpg');
        console.log("Sending image to server for authentication...");

        fetch(window.location.href, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response data:", data);
            isAuthenticating = false;

            if (data.error) {
                console.error("Authentication error:", data.error);
                status.textContent = data.error;
                status.style.color = 'red';
            } else {
                console.log("Authentication successful.");
                status.textContent = "Authentication successful!";
                status.style.color = 'green';

                // Stop further requests
                clearInterval(intervalId);

                setTimeout(() => {
                    console.log("Redirecting to dashboard...");
                    window.location.href = '/dashboard';
                }, 2000);
            }
        })
        .catch(err => {
            isAuthenticating = false;
            console.error("Error uploading image:", err);
            status.textContent = "Error uploading image. Please try again.";
            status.style.color = 'red';
        });
    }, 'image/jpeg');
}

// Continuously check for facial authentication every 2 seconds
intervalId = setInterval(authenticateFace, 2000);