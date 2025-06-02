from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import hashlib
import json
import time
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'mysecretkey'

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    return hashlib.sha256((password + salt).encode()).hexdigest(), salt

def generate_voter_id(raw_input):
    return hashlib.sha256(raw_input.strip().encode()).hexdigest()

# ---------------- Blockchain ----------------

class Blockchain:
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.create_block(voter_id="Genesis", candidate_id="Genesis", previous_hash='0')

    def create_block(self, voter_id, candidate_id, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'voter_id_hash': hashlib.sha256(voter_id.encode()).hexdigest(),
            'candidate_id': candidate_id,
            'previous_hash': previous_hash
        }
        block['hash'] = self.hash(block)
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def hash(self, block):
        block_string = json.dumps({k: v for k, v in block.items() if k != 'hash'}, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def is_chain_valid(self, chain):
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            if current['previous_hash'] != previous['hash']:
                return False
            if current['hash'] != self.hash(current):
                return False
        return True

    def register_node(self, address):
        parsed = urlparse(address)
        self.nodes.add(parsed.netloc)

    def replace_chain(self):
        longest = self.chain
        max_length = len(longest)
        for node in self.nodes:
            try:
                res = requests.get(f'http://{node}/chain')
                if res.status_code == 200:
                    length = len(res.json())
                    chain = res.json()
                    if length > max_length and self.is_chain_valid(chain):
                        longest = chain
                        max_length = length
            except Exception:
                continue
        if longest != self.chain:
            self.chain = longest
            return True
        return False

    def broadcast_block(self, block):
        for node in self.nodes:
            try:
                requests.post(f'http://{node}/receive_block', json=block)
            except Exception:
                pass

    def receive_block(self, block):
        last_block = self.get_previous_block()
        if block['previous_hash'] == last_block['hash']:
            self.chain.append(block)
            return True
        return False

# ---------------- Voting System ----------------

class VotingSystem:
    def __init__(self):
        self.candidates = {}
        self.voters = {}
        self.candidates_count = 0
        self.admin_hash = None
        self.salt = None
        self.voting_start = None
        self.voting_end = None
        self.audit_log = []
        self.blockchain = Blockchain()

    def initialize(self, admin_password):
        self.salt = os.urandom(16).hex()
        self.admin_hash = hash_password(admin_password, self.salt)
        self.add_candidate("Alice", "Supports education reform")
        self.add_candidate("Bob", "Focuses on economic growth")
        self.voting_start = datetime.now().date()
        self.voting_end = self.voting_start + timedelta(days=7)
        self.log_event("System initialized")

    def verify_admin(self, input_password):
        return self.admin_hash == hash_password(input_password.strip(), self.salt)

    def add_candidate(self, name, description=""):
        if self.admin_hash is None:
            raise PermissionError("Admin privileges required")
        self.candidates_count += 1
        self.candidates[self.candidates_count] = {
            "id": self.candidates_count,
            "name": name,
            "description": description,
            "votes": 0,
            "active": True
        }
        self.log_event(f"Candidate added: {name} (ID: {self.candidates_count})")

    def vote(self, voter_id, candidate_id):
        if datetime.now().date() < self.voting_start:
            raise ValueError("Voting period has not started")
        if datetime.now().date() > self.voting_end:
            raise ValueError("Voting period has ended")
        if voter_id in self.voters:
            raise ValueError("You have already voted!")
        if candidate_id not in self.candidates or not self.candidates[candidate_id]["active"]:
            raise ValueError("Invalid candidate selection!")

        self.voters[voter_id] = {
            "vote": candidate_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.candidates[candidate_id]["votes"] += 1
        self.log_event(f"Vote recorded: Voter {voter_id} voted for candidate {candidate_id}")

        # Blockchain vote
        previous_block = self.blockchain.get_previous_block()
        block = self.blockchain.create_block(voter_id, str(candidate_id), previous_block['hash'])
        self.blockchain.broadcast_block(block)

    def get_results(self):
        return [f"{c['id']}: {c['name']} - {c['votes']} votes ({'Active' if c['active'] else 'Inactive'})"
                for c in self.candidates.values()]

    def log_event(self, event):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.audit_log.append(f"{timestamp} - {event}")

    def set_voting_period(self, start_date, end_date):
        if start_date >= end_date:
            raise ValueError("End date must be after start date")
        self.voting_start = start_date
        self.voting_end = end_date
        self.log_event(f"Voting period set: {start_date} to {end_date}")

# Instantiate and initialize
voting_system = VotingSystem()
voting_system.initialize("admin123")

# ---------------- Routes ----------------

@app.route('/')
def index():
    candidates = [c for c in voting_system.candidates.values() if c['active']]
    return render_template('index.html',
                           candidates=candidates,
                           voting_start=voting_system.voting_start,
                           voting_end=voting_system.voting_end)

@app.route('/vote', methods=['POST'])
def vote():
    raw_input = request.form['voter_id']
    candidate_id = request.form['candidate_id']
    voter_id = generate_voter_id(raw_input)

    try:
        voting_system.vote(voter_id, int(candidate_id))
        flash("✅ Vote recorded successfully!", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "danger")
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    return render_template('admin.html',
                           voting_start=voting_system.voting_start,
                           voting_end=voting_system.voting_end)

@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    name = request.form.get('name')
    party = request.form.get('party')
    try:
        voting_system.add_candidate(name, party)
        flash("✅ Candidate added successfully!", "success")
    except Exception as e:
        flash(f"❌ Error adding candidate: {str(e)}", "danger")
    return redirect(url_for('admin'))

@app.route('/set_dates', methods=['POST'])
def set_dates():
    try:
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        voting_system.set_voting_period(start_date, end_date)
        flash("✅ Voting dates updated!", "success")
    except Exception as e:
        flash(f"❌ Error setting dates: {str(e)}", "danger")
    return redirect(url_for('admin'))

@app.route('/results')
def results():
    return render_template('results.html', results=voting_system.get_results())

@app.route('/chain')
def chain():
    return jsonify(voting_system.blockchain.chain), 200

@app.route('/register_node', methods=['POST'])
def register_node():
    data = request.get_json()
    node = data.get('node')
    if node is None:
        return 'Missing node address', 400
    voting_system.blockchain.register_node(node)
    return jsonify({'message': 'Node registered successfully'}), 201

@app.route('/replace_chain')
def replace_chain():
    replaced = voting_system.blockchain.replace_chain()
    message = "Chain was replaced" if replaced else "Chain is already up-to-date"
    return jsonify({'message': message, 'chain': voting_system.blockchain.chain})

@app.route('/receive_block', methods=['POST'])
def receive_block():
    block = request.get_json()
    success = voting_system.blockchain.receive_block(block)
    return jsonify({'message': 'Block added' if success else 'Invalid block'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)