import streamlit as st
import hashlib
import time
import json
import os

# File where blockchain will be save
BLOCKCHAIN_FILE = "blockchain_data.json"

# Set page configuration as the first Streamlit command
st.set_page_config(page_title="Login System", layout="wide")

# Blockchain setup
blockchain = []

# Initialize the blockchain with a genesis block
def initialize_blockchain():
    global blockchain
    if not blockchain:
        if os.path.exists(BLOCKCHAIN_FILE):
            # Load blockchain data from file if it exists
            with open(BLOCKCHAIN_FILE, 'r') as f:
                blockchain = json.load(f)
        else:
            # Create a genesis block if no file exists
            genesis_block = {
                "index": 0,
                "timestamp": time.time(),
                "product_details": [],
                "previous_hash": "0",
                "hash": "genesis_block"
            }
            blockchain.append(genesis_block)

# Hashing utility functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_file(file):
    file.seek(0)  # Ensure the file pointer is at the beginning
    return hashlib.sha256(file.read()).hexdigest()

def hash_block(block):
    block_string = f"{block['index']}{block['timestamp']}{block['product_details']}{block['previous_hash']}"
    return hashlib.sha256(block_string.encode()).hexdigest()

# Blockchain management
def add_block(product_details, barcode_hash):
    global blockchain
    previous_block = blockchain[-1]
    block = {
        "index": len(blockchain),
        "timestamp": time.time(),
        "product_details": [{"product": product_details, "barcode_hash": barcode_hash}],
        "previous_hash": previous_block["hash"],
        "hash": "temporary_placeholder"
    }
    block["hash"] = hash_block(block)
    blockchain.append(block)
    
    # Save blockchain to a file after adding a new block
    with open(BLOCKCHAIN_FILE, 'w') as f:
        json.dump(blockchain, f)

def verify_barcode_in_blockchain(barcode_hash):
    for block in blockchain:
        for product in block["product_details"]:
            if product["barcode_hash"] == barcode_hash:
                return True
    return False

# Authentication
users = {
    "manu": hash_password("manu123"),
    "user": hash_password("user123")
}
roles = {
    "manu": "manufacturer",
    "user": "user"
}

def login(username, password):
    hashed_password = hash_password(password)
    if username in users and users[username] == hashed_password:
        return roles[username]
    return None

# Manufacturer Dashboard
def manufacturer_dashboard():
    st.title("Manufacturer Dashboard")
    st.subheader("Welcome, Manufacturer!")

    with st.form("product_form"):
        product_name = st.text_input("Product Name")
        manufacturer_name = st.text_input("Manufacturer Name")
        barcode_file = st.file_uploader("Upload Barcode", type=["png", "jpg", "jpeg", "pdf", "txt"])
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if product_name and manufacturer_name and barcode_file:
                barcode_hash = hash_file(barcode_file)
                product_details = {
                    "product_name": product_name,
                    "manufacturer_name": manufacturer_name
                }
                add_block(product_details, barcode_hash)
                st.success(f"Product added successfully with Barcode Hash: {barcode_hash}")
            else:
                st.error("Please fill in all the fields and upload a barcode file.")

# User Dashboard
def user_dashboard():
    st.title("User Dashboard")
    st.subheader("Welcome, User!")
    st.write("Check if a barcode exists in the blockchain.")

    barcode_file = st.file_uploader("Upload Barcode to Verify", type=["png", "jpg", "jpeg", "pdf", "txt"])
    if barcode_file:
        barcode_hash = hash_file(barcode_file)
        st.write(f"Barcode Hash: {barcode_hash}")
        
        if verify_barcode_in_blockchain(barcode_hash):
            st.success("Barcode is available in the blockchain!")
        else:
            st.error("Barcode is not available in the blockchain.")

# Main Application
def main():
    session = st.session_state

    # Initialize session state if not already done
    if "logged_in" not in session:
        session.logged_in = False
        session.role = None

    if session.logged_in:
        if session.role == "manufacturer":
            manufacturer_dashboard()
        elif session.role == "user":
            user_dashboard()

        if st.button("Logout"):
            session.logged_in = False
            session.role = None
            # Clearing session state and effectively logging out
            session.clear()

    else:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            role = login(username, password)
            if role:
                session.logged_in = True
                session.role = role
                # No rerun required, just rely on session state to determine the page content
                st.session_state.logged_in = True
                st.session_state.role = role
            else:
                st.error("Invalid username or password.")

if __name__ == "__main__":
    initialize_blockchain()
    main()
