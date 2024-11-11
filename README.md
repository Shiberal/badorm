# BAD ORM

A simple Python package for SQLite operations with Pydantic models.

## Installation 

```bash
pip install sqlite-operations
```

## Usage

### Basic Example

```python
from datetime import date, time
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from operations.sqlite.operations import Operations
from database.sqlite_conn import SqliteConn

# Define your model
class Product(BaseModel):
    id: UUID = uuid4()  # Auto-generated UUID
    name: str
    price: Decimal
    in_stock: bool
    manufacture_date: date
    restock_time: time
    description: Optional[str] = None

# Initialize database connection
db = SqliteConn("products.db")
product_ops = Operations(Product, db)

# Create the table
product_ops.makeTable()

# Create a product
new_product = Product(
    name="Laptop",
    price=Decimal("999.99"),
    in_stock=True,
    manufacture_date=date(2024, 1, 15),
    restock_time=time(9, 0, 0),
    description="High-performance laptop"
)

# Insert into database
product_ops.create(new_product.model_dump())

# Read a product by ID
product = product_ops.read(new_product.id)
print(f"Found product: {product.name}")

# Update a product
updates = {"price": Decimal("899.99"), "in_stock": False}
product_ops.update(new_product.id, updates)

# Read all products
all_products = product_ops.read_all()
for p in all_products:
    print(f"{p.name}: ${p.price}")

# Delete a product
product_ops.delete(new_product.id)
```

### Features

- Automatic table creation from Pydantic models
- UUID primary keys
- Support for various data types:
  - Strings
  - Integers
  - Decimals
  - Booleans
  - Dates
  - Times
  - Optional fields
- CRUD operations (Create, Read, Update, Delete)
- SQL injection protection through parameterized queries

### Advanced Usage

```python
# Read by specific field
products = product_ops.read_by_field("in_stock", True)
print("In-stock products:", [p.name for p in products])

# Batch creation
products = [
    Product(
        name="Mouse",
        price=Decimal("29.99"),
        in_stock=True,
        manufacture_date=date(2024, 2, 1),
        restock_time=time(14, 30, 0)
    ),
    Product(
        name="Keyboard",
        price=Decimal("59.99"),
        in_stock=True,
        manufacture_date=date(2024, 2, 1),
        restock_time=time(14, 30, 0)
    )
]

for product in products:
    product_ops.create(product.model_dump())
```

## Data Type Support

The ORM supports the following Python types:
- `str`
- `int`
- `float`
- `bool`
- `date`
- `time`
- `datetime`
- `Decimal`
- `UUID`
- `bytes`
- `Optional` versions of all above types

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.