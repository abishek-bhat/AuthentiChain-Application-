import streamlit as st
import hashlib
import time
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt

# File where blockchain and user data will be saved
BLOCKCHAIN_FILE = "blockchain_data.json"
USERS_FILE = "users.json"

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

# PDF Generation
def generate_blockchain_pdf(blockchain_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    
    y = height - 50  # Start near the top of the page
    c.drawString(50, y, "Blockchain Data")
    y -= 20

    for block in blockchain_data:
        for product in block['product_details']:
            product_name = product['product']['product_name']
            manufacturer_name = product['product']['manufacturer_name']
            barcode_hash = product['barcode_hash']

            # Display product details in PDF
            c.drawString(50, y, f"Product Name: {product_name}")
            y -= 15
            c.drawString(50, y, f"Manufacturer: {manufacturer_name}")
            y -= 15
            c.drawString(50, y, f"Barcode Hash: {barcode_hash}")
            y -= 20

            if y < 50:  # Start a new page if space runs out
                c.showPage()
                y = height - 50

    c.save()
    buffer.seek(0)
    return buffer

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

def create_account(username, password, role):
    if username not in users:
        users[username] = hash_password(password)
        roles[username] = role
        # Save users to a file to persist the new account
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        st.success(f"Account created successfully with role '{role}'!")
    else:
        st.error("Username already exists. Please choose a different username.")

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
    
    if st.button("Download Blockchain as PDF"):
        pdf_buffer = generate_blockchain_pdf(blockchain)
        st.download_button(
            label="Download Blockchain PDF",
            data=pdf_buffer,
            file_name="blockchain_data.pdf",
            mime="application/pdf"
        )

# User Dashboard
def user_dashboard():
    st.title("User Dashboard")
    st.subheader("Welcome, User!")
    st.write("Check if a barcode exists in the blockchain.")

    # Search section for User Dashboard
    search_type = st.radio("Search by", ["Manufacturer Name", "Product Name"])

    search_term = st.text_input(f"Enter {search_type}")
    if st.button("Search"):
        if search_term:
            found = False
            search_results = []
            for block in blockchain:
                for product in block["product_details"]:
                    if search_type == "Manufacturer Name" and product["product"]["manufacturer_name"] == search_term:
                        search_results.append({
                            "Product Name": product['product']['product_name'],
                            "Manufacturer": product['product']['manufacturer_name'],
                            "Barcode Hash": product['barcode_hash']
                        })
                        found = True
                    elif search_type == "Product Name" and product["product"]["product_name"] == search_term:
                        search_results.append({
                            "Product Name": product['product']['product_name'],
                            "Manufacturer": product['product']['manufacturer_name'],
                            "Barcode Hash": product['barcode_hash']
                        })
                        found = True

            if found:
                st.write("Search Results:")
                st.dataframe(pd.DataFrame(search_results))
            else:
                st.error(f"No product found with {search_type}: {search_term}")
        else:
            st.error(f"Please enter a {search_type} to search.")
    
    barcode_file = st.file_uploader("Upload Barcode to Verify", type=["png", "jpg", "jpeg", "pdf", "txt"])
    if barcode_file:
        barcode_hash = hash_file(barcode_file)
        st.write(f"Barcode Hash: {barcode_hash}")
        
        if verify_barcode_in_blockchain(barcode_hash):
            st.success("Barcode is available in the blockchain!")
        else:
            st.error("Barcode is not available in the blockchain.")
    
    if st.button("Download Blockchain as PDF"):
        pdf_buffer = generate_blockchain_pdf(blockchain)
        st.download_button(
            label="Download Blockchain PDF",
            data=pdf_buffer,
            file_name="blockchain_data.pdf",
            mime="application/pdf"
        )

# Analytics function
def show_analytics():
    # Calculate analytics
    product_count = sum(len(block['product_details']) for block in blockchain)
    manufacturers = [product['product']['manufacturer_name'] for block in blockchain for product in block['product_details']]
    unique_barcodes = set(product['barcode_hash'] for block in blockchain for product in block['product_details'])
    
    most_frequent_manufacturer = pd.Series(manufacturers).mode()[0]
    
    st.subheader(" Analytics")
    st.write(f"Product Count: {product_count}")
    st.write(f"Most Frequent Manufacturer: {most_frequent_manufacturer}")
    st.write(f"Unique Barcodes: {len(unique_barcodes)}")
    
    # Visualizations
    st.subheader("Analytics Visualization")
    
    # Bar chart for product count per manufacturer
    manufacturer_counts = pd.Series(manufacturers).value_counts()
    st.bar_chart(manufacturer_counts)
    
    # Line chart for product count over time (using timestamp as index)
    timestamps = [block['timestamp'] for block in blockchain]
    product_counts_over_time = [len(block['product_details']) for block in blockchain]
    df = pd.DataFrame({'Timestamp': timestamps, 'Product Count': product_counts_over_time})
    df = df.sort_values(by='Timestamp')
    st.line_chart(df.set_index('Timestamp')['Product Count'])
    
    # Pie chart for distribution of product counts across manufacturers
    manufacturer_distribution = manufacturer_counts.head(10)  # Top 10 manufacturers
    st.write("Top 10 Manufacturers Distribution")
    st.write(manufacturer_distribution)
    
    # Pie chart for the manufacturer distribution
    fig, ax = plt.subplots()
    ax.pie(manufacturer_distribution, labels=manufacturer_distribution.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

# Blockchain Visualization
def visualize_blockchain():
    st.subheader("Blockchain Visualization")
    st.write("Visualizing the blockchain as a network of blocks connected to each other.")

    # Simple visualization of blockchain structure
    block_indexes = [block['index'] for block in blockchain]
    previous_hashes = [block['previous_hash'] for block in blockchain]
    current_hashes = [block['hash'] for block in blockchain]

    df = pd.DataFrame({
        'Block Index': block_indexes,
        'Previous Hash': previous_hashes,
        'Current Hash': current_hashes
    })

    st.write("Blockchain Structure:")
    st.dataframe(df)
    
    # Bar chart for the number of products in each block
    fig, ax = plt.subplots()
    ax.bar(block_indexes, [len(block['product_details']) for block in blockchain], color='b')
    ax.set_title('Number of Products in Each Block')
    ax.set_xlabel('Block Index')
    ax.set_ylabel('Number of Products')
    st.pyplot(fig)


# Main Application
def main():
    session = st.session_state

    # Initialize session state if not already done
    if "logged_in" not in session:
        session.logged_in = False
        session.role = None
    if "create_account" not in session:
        session.create_account = False

    # Sidebar navigation with radio button
    page = st.sidebar.radio("Select a page:", ["Login", "Analytics", "Create Account", "View Blockchain Visualization"])

    if page == "Login":
        if session.logged_in:
            if session.role == "manufacturer":
                manufacturer_dashboard()
            elif session.role == "user":
                user_dashboard()

            if st.button("Logout"):
                session.logged_in = False
                session.role = None
                st.success("Logged out successfully.")

        else:
            st.title("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.button("Login")

            if submit_button:
                role = login(username, password)
                if role:
                    session.logged_in = True
                    session.role = role
                    st.success(f"Logged in successfully as {role}!")
                    if role == "manufacturer":
                        manufacturer_dashboard()
                    elif role == "user":
                        user_dashboard()
                else:
                    st.error("Invalid username or password.")
    
    elif page == "Analytics":
        show_analytics()

    elif page == "Create Account":
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        role = st.selectbox("Select Role", ["manufacturer", "user"])
        create_button = st.button("Create Account")

        if create_button:
            create_account(username, password, role)

    elif page == "View Blockchain Visualization":
        visualize_blockchain()

if __name__ == "__main__":
    initialize_blockchain()
    main()
