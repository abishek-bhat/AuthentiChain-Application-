This script is a blockchain-based product tracking system with the following functionality:

### Key Features:
1. **Blockchain Initialization**:
   - A genesis block is created if no blockchain exists.
   - Blocks contain details about products (name, manufacturer, and barcode hash) and maintain cryptographic integrity using SHA-256 hashing.

2. **Authentication System**:
   - **Login**: Users are authenticated using hashed passwords stored in a JSON file.
   - **Account Creation**: New users can create accounts with roles (`Manufacturer` or `User`).

3. **Manufacturer Dashboard**:
   - Allows manufacturers to add products by uploading barcode files.
   - Each product is hashed and added to the blockchain.
   - Generates a PDF of blockchain data for download.

4. **User Dashboard**:
   - Enables users to search for products by manufacturer name or product name.
   - Allows barcode verification to check if a product exists in the blockchain.
   - Provides the ability to download blockchain data as a PDF.

5. **Blockchain Analytics**:
   - Computes statistics such as the total number of products, unique barcodes, and the most frequent manufacturer.
   - Provides visualizations, including:
     - A bar chart for product counts per manufacturer.
     - Time-based product addition trends.

6. **PDF Export**:
   - Generates a PDF containing detailed blockchain data for sharing or record-keeping.

7. **Streamlit Integration**:
   - User-friendly web interface for all actions, including login, product addition, and analytics visualization.

### Functions Overview:
- **Hashing Functions**:
  - Passwords and files are hashed to ensure data security and integrity.
  
- **Blockchain Management**:
  - Tracks products using blocks and verifies the uniqueness of barcodes.

- **PDF Generation**:
  - Converts blockchain data into a downloadable PDF format.

- **Authentication**:
  - Securely manages user credentials and roles.

- **Analytics and Visualization**:
  - Provides insights into blockchain data through text summaries and charts.

### User Roles:
- **Manufacturer**:
  - Adds new products with hashed barcodes.
  - Downloads the blockchain as a PDF.

- **User**:
  - Searches for and verifies products.
  - Views blockchain analytics and downloads the blockchain as a PDF.

### Visualization:
- Displays blockchain analytics, including product counts and manufacturer statistics, using charts.

This system is suitable for product tracking in supply chains or inventory management, where data immutability and secure tracking are required.
