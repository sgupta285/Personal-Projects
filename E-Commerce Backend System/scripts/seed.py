"""
Seed the database with sample categories, products, and customers.
Run: python -m scripts.seed
"""

import asyncio
import random
from app.models.database import init_db, async_session
from app.models.orm import Category, Product, Customer, gen_id

CATEGORIES = [
    ("Electronics", "Phones, laptops, gadgets"),
    ("Clothing", "Men's and women's apparel"),
    ("Home & Kitchen", "Furniture, appliances, decor"),
    ("Books", "Fiction, non-fiction, textbooks"),
    ("Sports", "Equipment, apparel, accessories"),
    ("Toys", "Games, puzzles, outdoor toys"),
]

ADJECTIVES = ["Premium", "Ultra", "Pro", "Classic", "Deluxe", "Essential", "Elite", "Eco"]
PRODUCT_TEMPLATES = {
    "Electronics": ["Wireless Headphones", "Bluetooth Speaker", "Smart Watch", "USB Hub", "Webcam", "Power Bank", "Keyboard", "Mouse"],
    "Clothing": ["T-Shirt", "Hoodie", "Jeans", "Jacket", "Sneakers", "Cap", "Socks Pack", "Polo Shirt"],
    "Home & Kitchen": ["Coffee Maker", "Blender", "Desk Lamp", "Throw Pillow", "Cutting Board", "Water Bottle", "Pan Set", "Towel Set"],
    "Books": ["Data Science Handbook", "Python Cookbook", "Design Patterns", "Algorithms Guide", "ML Engineering", "System Design", "Clean Code", "AI Primer"],
    "Sports": ["Yoga Mat", "Dumbbells", "Running Shoes", "Resistance Bands", "Jump Rope", "Gym Bag", "Water Bottle", "Fitness Tracker"],
    "Toys": ["Building Blocks", "Puzzle Set", "Board Game", "RC Car", "Art Kit", "Science Kit", "Card Game", "Plush Toy"],
}

CUSTOMER_NAMES = [
    ("Alice Johnson", "alice@example.com"),
    ("Bob Smith", "bob@example.com"),
    ("Carol Williams", "carol@example.com"),
    ("David Brown", "david@example.com"),
    ("Eva Martinez", "eva@example.com"),
    ("Frank Lee", "frank@example.com"),
    ("Grace Kim", "grace@example.com"),
    ("Henry Chen", "henry@example.com"),
    ("Iris Patel", "iris@example.com"),
    ("Jack Wilson", "jack@example.com"),
]


async def seed():
    await init_db()

    async with async_session() as session:
        # Categories
        cat_map = {}
        for name, desc in CATEGORIES:
            cat = Category(id=gen_id(), name=name, description=desc)
            session.add(cat)
            cat_map[name] = cat

        await session.flush()

        # Products (~50 products)
        sku_counter = 1000
        for cat_name, templates in PRODUCT_TEMPLATES.items():
            for template in templates:
                adj = random.choice(ADJECTIVES)
                product = Product(
                    id=gen_id(),
                    name=f"{adj} {template}",
                    description=f"High-quality {template.lower()} in our {cat_name.lower()} collection.",
                    price=round(random.uniform(9.99, 299.99), 2),
                    stock=random.randint(10, 500),
                    sku=f"SKU-{sku_counter:05d}",
                    category_id=cat_map[cat_name].id,
                    is_active=True,
                )
                session.add(product)
                sku_counter += 1

        # Customers
        for name, email in CUSTOMER_NAMES:
            customer = Customer(id=gen_id(), email=email, name=name)
            session.add(customer)

        await session.commit()
        print(f"Seeded: {len(CATEGORIES)} categories, {sum(len(v) for v in PRODUCT_TEMPLATES.values())} products, {len(CUSTOMER_NAMES)} customers")


if __name__ == "__main__":
    asyncio.run(seed())
