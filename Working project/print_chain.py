import hashlib
import datetime
import streamlit as st

# Block and Blockchain Classes
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def create_genesis_block(self):
        return Block(0, datetime.datetime.now(), "Genesis Block", "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), datetime.datetime.now(), data, latest_block.hash)
        self.chain.append(new_block)
    
    def get_blocks(self):
        return self.chain

# Streamlit App
def display_blockchain(blockchain):
    st.title("📦 Blockchain Viewer with Boxes and Lines")
    st.markdown("""
        <style>
        .block {
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 15px;
            margin: 10px auto;
            background-color: #f9f9f9;
            color: black; /* Text color set to black */
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
        }
        .line {
            width: 2px;
            height: 40px;
            background-color: #4CAF50;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render blocks and lines
    for i, block in enumerate(blockchain.get_blocks()):
        # Display block
        st.markdown(f"""
            <div class="block">
                <h4>Block Index: {block.index}</h4>
                <p><strong>Timestamp:</strong> {block.timestamp}</p>
                <p><strong>Data:</strong> {block.data}</p>
                <p><strong>Previous Hash:</strong> {block.previous_hash}</p>
                <p><strong>Hash:</strong> {block.hash}</p>
            </div>
        """, unsafe_allow_html=True)

        # Add a connecting line (except after the last block)
        if i < len(blockchain.get_blocks()) - 1:
            st.markdown('<div class="line"></div>', unsafe_allow_html=True)

# Main
if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.add_block("First Block")
    blockchain.add_block("Second Block")
    blockchain.add_block("Third Block")
    
    display_blockchain(blockchain)
