# 🗳️ Blockchain-Based Voting System

A secure and tamper-proof voting platform built using **Flask**, a **Python-based blockchain**, and a web-based admin panel. Designed for transparency and trust, each vote is recorded immutably on a local blockchain with features like candidate management, voting period control, and live results display.

## 🚀 Features

- 🔐 **Secure Voting** — Voter IDs are hashed using SHA-256.
- ⛓️ **Blockchain Integrity** — Each vote is stored as a verifiable block.
- 🧑‍💼 **Admin Panel** — Add candidates and set voting dates.
- 📊 **Live Results** — Real-time vote count and status.
- 🧾 **Audit Trail** — Internal log of system events.
- 🌐 **Simple UI** — Clean and responsive interface with Tailwind CSS.


## 🧠 Technologies Used

| Area        | Tools & Libraries                     |
|-------------|----------------------------------------|
| Backend     | Python, Flask, SHA-256, requests       |
| Frontend    | HTML, Tailwind CSS, Jinja2 templates   |
| Blockchain  | Custom Python blockchain               |
| Optional    | Solidity (`Voting.sol` for future dApp) |

## 📦 How It Works

1. **User visits** the home page and casts their vote.
2. **Voter ID is hashed** and validated for uniqueness.
3. **Vote is recorded** on the custom blockchain.
4. **Admin** manages candidates and voting dates via panel.
5. **Results page** shows real-time voting tally.

## 🛠️ Setup Instructions

### 1. Install Python
```
- 📥 [Download Python]
```
### 2. Clone This Repository

```bash
git clone https://github.com/abhi100om/blockchain-voting-system.git
cd blockchain-voting-system
```
### 3. Install Dependencies
```
pip install flask requests
```
### 4. Run the Application
```
python app.py
```
App will start on `http://localhost:5000`.
### 5. Access the Frontend
```
Open your browser and navigate to:
http://localhost:5000
```
## 📊 Admin Dashboard

- URL: `/admin`
- Features:
  - Add new candidates
  - Set voting start & end dates
  - View live results
- Default Admin Password: `admin123` (set in `app.py`)

## 🔗 Blockchain API Endpoints

| Endpoint            | Method | Description                            |
|---------------------|--------|----------------------------------------|
| `/chain`            | GET    | View the full blockchain               |
| `/receive_block`    | POST   | Receive a block from another node      |
| `/register_node`    | POST   | Register a new node in the network     |
| `/replace_chain`    | GET    | Consensus algorithm (replace if needed)|

## 💡 Future Improvements

- [ ] OTP/email verification for voters
- [ ] Blockchain explorer UI
- [ ] Ethereum smart contract (`Voting.sol`) integration
- [ ] Anonymous vote shuffling / zero-knowledge enhancements
- [ ] Docker container for deployment

## 📝 License

This project is licensed under the [MIT License](LICENSE).
