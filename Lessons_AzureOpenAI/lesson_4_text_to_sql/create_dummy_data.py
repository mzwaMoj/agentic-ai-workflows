import pandas as pd
import numpy as np
from faker import Faker
import uuid
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Set seed for reproducibility
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def create_customers_data(n=1000):
    """Create dummy customer data"""
    customers = []
    for i in range(n):
        customer = {
            'customer_id': fake.uuid4(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=80),
            'address': fake.address().replace('\n', ', '),
            'city': fake.city(),
            'state': fake.state(),
            'country': fake.country(),
            'registration_date': fake.date_between(start_date='-2y', end_date='today'),
            'customer_status': random.choice(['Active', 'Inactive', 'Premium']),
            'total_spent': round(random.uniform(10, 5000), 2)
        }
        customers.append(customer)
    return pd.DataFrame(customers)

def create_products_data(n=200):
    """Create dummy product data"""
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Beauty', 'Toys', 'Food']
    products = []
    
    for i in range(n):
        category = random.choice(categories)
        product = {
            'product_id': str(uuid.uuid4()),
            'product_name': fake.catch_phrase(),
            'category': category,
            'price': round(random.uniform(5, 1000), 2),
            'cost': round(random.uniform(2, 500), 2),
            'stock_quantity': random.randint(0, 1000),
            'supplier': fake.company(),
            'description': fake.text(max_nb_chars=200),
            'created_date': fake.date_between(start_date='-1y', end_date='today'),
            'is_active': random.choice([True, False])
        }
        # Ensure cost is less than price
        product['cost'] = min(product['cost'], product['price'] * 0.7)
        products.append(product)
    return pd.DataFrame(products)

def create_orders_data(customers_df, products_df, n=2000):
    """Create dummy order data"""
    orders = []
    
    for i in range(n):
        customer = customers_df.sample(1).iloc[0]
        order_date = fake.date_between(start_date='-1y', end_date='today')
        
        order = {
            'order_id': str(uuid.uuid4()),
            'customer_id': customer['customer_id'],
            'order_date': order_date,
            'status': random.choice(['Pending', 'Shipped', 'Delivered', 'Cancelled']),
            'total_amount': 0,  # Will be calculated based on order items
            'shipping_address': fake.address().replace('\n', ', '),
            'payment_method': random.choice(['Credit Card', 'PayPal', 'Bank Transfer', 'Cash'])
        }
        orders.append(order)
    return pd.DataFrame(orders)

def create_order_items_data(orders_df, products_df, avg_items_per_order=2.5):
    """Create dummy order items data"""
    order_items = []
    
    for _, order in orders_df.iterrows():
        num_items = max(1, int(np.random.poisson(avg_items_per_order)))
        selected_products = products_df.sample(min(num_items, len(products_df)))
        
        order_total = 0
        for _, product in selected_products.iterrows():
            quantity = random.randint(1, 5)
            unit_price = product['price']
            total_price = quantity * unit_price
            order_total += total_price
            
            item = {
                'item_id': str(uuid.uuid4()),
                'order_id': order['order_id'],
                'product_id': product['product_id'],
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            }
            order_items.append(item)
        
        # Update order total
        orders_df.loc[orders_df['order_id'] == order['order_id'], 'total_amount'] = round(order_total, 2)
    
    return pd.DataFrame(order_items)

def create_reviews_data(customers_df, products_df, n=1500):
    """Create dummy review data"""
    reviews = []
    
    for i in range(n):
        customer = customers_df.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]
        
        review = {
            'review_id': str(uuid.uuid4()),
            'customer_id': customer['customer_id'],
            'product_id': product['product_id'],
            'rating': random.randint(1, 5),
            'review_text': fake.text(max_nb_chars=300),
            'review_date': fake.date_between(start_date='-1y', end_date='today'),
            'helpful_votes': random.randint(0, 50)
        }
        reviews.append(review)
    return pd.DataFrame(reviews)

def main():
    """Generate all dummy data and save to CSV files"""
    print("Generating dummy data...")
    
    # Create data
    customers_df = create_customers_data(1000)
    products_df = create_products_data(200)
    orders_df = create_orders_data(customers_df, products_df, 2000)
    order_items_df = create_order_items_data(orders_df, products_df)
    reviews_df = create_reviews_data(customers_df, products_df, 1500)
    
    # Save to CSV files
    save_path = './lesson_4_text_to_sql/dataset/'
    customers_df.to_csv(save_path+'customers.csv', index=False)
    products_df.to_csv(save_path+'products.csv', index=False)
    orders_df.to_csv(save_path+'orders.csv', index=False)
    order_items_df.to_csv(save_path+'order_items.csv', index=False)
    reviews_df.to_csv(save_path+'reviews.csv', index=False)
    
    print("Data generation complete!")
    print(f"Generated {len(customers_df)} customers")
    print(f"Generated {len(products_df)} products")
    print(f"Generated {len(orders_df)} orders")
    print(f"Generated {len(order_items_df)} order items")
    print(f"Generated {len(reviews_df)} reviews")
    
    # Display sample data
    print("\nSample data:")
    print("\nCustomers:")
    print(customers_df.head())
    print("\nProducts:")
    print(products_df.head())
    print("\nOrders:")
    print(orders_df.head())

if __name__ == "__main__":
    main()
