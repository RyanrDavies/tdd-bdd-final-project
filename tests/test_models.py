# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a product from the database"""
        product = ProductFactory()
        app.logger.info(f"Testing read a product with product: {product}")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        read_product = Product.find(product.id)
        self.assertEqual(read_product.id, product.id)
        self.assertEqual(read_product.name, product.name)
        self.assertEqual(read_product.description, product.description)
        self.assertEqual(read_product.price, product.price)
        self.assertEqual(read_product.available, product.available)
        self.assertEqual(read_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        app.logger.info(f"Testing update a product with product: {product}")
        self.assertIsNotNone(product.id)
        original_id = product.id
        new_description = "New product description"
        product.description = new_description
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, new_description)
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, product.id)
        self.assertEqual(products[0].description, product.description)
    
    def test_invalid_update_a_product(self):
        """It should raise error when updating"""
        product = ProductFactory()
        product.id = None
        product.create()
        app.logger.info(f"Testing update a product with product: {product}")
        self.assertIsNotNone(product.id)
        product.id = None
        new_description = "New product description"
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        num_products = 5
        for _ in range(num_products):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        self.assertEqual(len(products), num_products)

    def test_find_by_name(self):
        """It should fetch products by name"""
        product_batch = []
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
            product_batch.append(product)
        first_product_name = product_batch[0].name
        names = [p.name for p in product_batch]
        expected_count = names.count(first_product_name)
        found_products = Product.find_by_name(first_product_name)
        self.assertEqual(found_products.count(), expected_count)
        for found_product in found_products:
            self.assertEqual(found_product.name, first_product_name)

    def test_find_by_availability(self):
        """It should fetch products by availability"""
        product_batch = []
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            product_batch.append(product)
        first_product_availability = product_batch[0].available
        availabilities = [p.available for p in product_batch]
        expected_count = availabilities.count(first_product_availability)
        found_products = Product.find_by_availability(first_product_availability)
        self.assertEqual(found_products.count(), expected_count)
        for found_product in found_products:
            self.assertEqual(found_product.available, first_product_availability)

    def test_find_by_category(self):
        """It should fetch products by category"""
        product_batch = []
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            product_batch.append(product)
        first_product_category = product_batch[0].category
        categories = [p.category for p in product_batch]
        expected_count = categories.count(first_product_category)
        found_products = Product.find_by_category(first_product_category)
        self.assertEqual(found_products.count(), expected_count)
        for found_product in found_products:
            self.assertEqual(found_product.category, first_product_category)
    
    def test_find_by_price(self):
        """It should fetch products by price"""
        product_batch = []
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            product_batch.append(product)
        first_product_price = product_batch[0].price
        prices = [p.price for p in product_batch]
        expected_count = prices.count(first_product_price)
        found_products = Product.find_by_price(first_product_price)
        self.assertEqual(found_products.count(), expected_count)
        for found_product in found_products:
            self.assertEqual(found_product.price, first_product_price)

    def test_find_by_string_price(self):
        """It should fetch products by string price"""
        product_batch = []
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            product_batch.append(product)
        first_product_price = product_batch[0].price
        prices = [p.price for p in product_batch]
        expected_count = prices.count(first_product_price)
        # Convert first_product_price to string before searching
        found_products = Product.find_by_price(str(first_product_price))
        self.assertEqual(found_products.count(), expected_count)
        for found_product in found_products:
            self.assertEqual(found_product.price, first_product_price)

    def test_deserialize_invalid_key(self):
        """It should raise an error if key is missing"""
        product = ProductFactory()
        product_dict = product.serialize()
        product_dict.pop('category')
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

    def test_deserialize_invalid_availability(self):
        """It should raise an error if available is not bool"""
        product = ProductFactory()
        product_dict = product.serialize()
        product_dict['available'] = None
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

    def test_deserialize_invalid_type(self):
        """It should raise an error if attribute is unknown"""
        product = ProductFactory()
        product_dict = product.serialize()
        self.assertRaises(DataValidationError, product.deserialize, None)
      
    def test_deserialize_invalid_attribute(self):
        """It should raise an error if attribute is unknown"""
        product = ProductFactory()
        product_dict = product.serialize()
        product_dict['category'] = "invalid"
        self.assertRaises(DataValidationError, product.deserialize, product_dict)
      
