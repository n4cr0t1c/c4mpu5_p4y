# CampusPay 💳

**CampusPay** is a facial authentication-based payment system that allows users to register, add funds, and securely transfer money using facial recognition.

---

## 🔐 Features

* **User Registration**: Sign up with name, date of birth, gender, and SRN (Student Registration Number).
* **Facial Authentication**: Log in and authorize transactions with facial recognition.
* **Add Funds**: Easily add money to your CampusPay wallet using Stripe.
* **Transfer Funds**: Instantly and securely send money to other registered users.

---

## 🛠️ Prerequisites

Before running the project, ensure you have the following installed:

* Python 3.8+
* Flask
* SQLite
* Stripe API keys (for payments)
* CMake (required for installing `dlib`, used in facial recognition)

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/campuspay.git
cd campuspay
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # On Linux/Mac
venv\Scripts\activate           # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install CMake

#### For Linux:

```bash
sudo apt update
sudo apt install -y cmake
```

#### For Windows:

* Download CMake from the [official website](https://cmake.org/download/).
* Install it and ensure it’s added to your system’s `PATH`.

---

## 🔑 Stripe Configuration

Update the `routes.py` file with your Stripe keys:

```python
STRIPE_SECRET_KEY = "your_secret_key"
STRIPE_PUBLISHABLE_KEY = "your_publishable_key"
```

---

## 🚀 Running the App

```bash
python run.py
```

Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📸 Facial Recognition Note

CampusPay uses facial recognition for authentication. Make sure your device has a working camera and permissions are enabled.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---
