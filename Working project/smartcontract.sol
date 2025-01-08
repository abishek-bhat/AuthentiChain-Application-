// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProductVerification {

    struct Product {
        string name;
        string barcodeHash;
        string productDetail1;
        string productDetail2;
        bool isRegistered;
    }

    mapping(string => Product) public products; // mapping from barcode hash to product details

    // Register a product by manufacturer
    function registerProduct(string memory barcodeHash, string memory name, string memory productDetail1, string memory productDetail2) public {
        require(!products[barcodeHash].isRegistered, "Product is already registered.");

        products[barcodeHash] = Product({
            name: name,
            barcodeHash: barcodeHash,
            productDetail1: productDetail1,
            productDetail2: productDetail2,
            isRegistered: true
        });
    }

    // Verify if a product is registered
    function verifyProduct(string memory barcodeHash) public view returns (string memory, string memory, string memory, string memory) {
        if (products[barcodeHash].isRegistered) {
            Product memory product = products[barcodeHash];
            return (product.name, product.productDetail1, product.productDetail2, "Original");
        } else {
            return ("", "", "", "Counterfeit");
        }
    }
}
