# CampusPay

CampusPay is a facial authentication-based payment system that allows users to register, add funds, and transfer money securely using facial recognition.

---

## Features

- **User Registration**: Users can register with their name, date of birth, gender, and SRN.
- **Facial Authentication**: Users log in and authenticate transactions using facial recognition.
- **Add Funds**: Users can add funds to their account via Stripe.
- **Transfer Funds**: Users can securely transfer funds to other users.

---

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.8+**
- **Flask**
- **SQLite**
- **Stripe API Keys**
- **CMake** (required for `dlib` installation)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/campuspay.git
cd campuspay

python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows

pip install -r [requirements.txt]


For Linux
sudo apt update
sudo apt install -y cmake

For Windows
Download CMake from the official website.
Install CMake and add it to your system's PATH.

In the routes.py change your
STRIPE_SECRET_KEY=your_secret_key
STRIPE_PUBLISHABLE_KEY=your_publishable_key

python run.py

http://127.0.0.1:5000