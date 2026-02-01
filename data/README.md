# Database Setup

## Olist SQLite Database

The `olist.sqlite` database file is **not included** in this repository due to GitHub's 100MB file size limit.

### Option 1: Download the Database

You can download the Olist E-commerce dataset from:
- [Kaggle: Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

After downloading, place the SQLite database file in this `data/` directory as `olist.sqlite`.

### Option 2: Use the Schema Only

The database schema is documented in `schema_output.md`. You can:
1. Create an empty SQLite database
2. Use the schema documentation to understand the table structure
3. Import your own data

### Option 3: Use Sample Data

For testing purposes, you can create a minimal database with sample data. The application will work with any SQLite database that follows the Olist schema structure.

## Database Schema

See `schema_output.md` for complete table definitions and relationships.

## Important Notes

- The database file should be named `olist.sqlite`
- Place it in the `data/` directory
- The application expects the database at: `data/olist.sqlite`
- Database size: ~107 MB (too large for GitHub)
