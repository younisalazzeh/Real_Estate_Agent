Database: olist.sqlite
============================================================

Table: product_category_name_translation
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
product_category_name TEXT            NO                        
product_category_name_english TEXT            NO                        

Total rows: 71

Table: sellers
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
seller_id            TEXT            NO                        
seller_zip_code_prefix INTEGER         NO                        
seller_city          TEXT            NO                        
seller_state         TEXT            NO                        

Total rows: 3095

Table: customers
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
customer_id          TEXT            NO                        
customer_unique_id   TEXT            NO                        
customer_zip_code_prefix INTEGER         NO                        
customer_city        TEXT            NO                        
customer_state       TEXT            NO                        

Total rows: 99441

Table: geolocation
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
geolocation_zip_code_prefix INTEGER         NO                        
geolocation_lat      REAL            NO                        
geolocation_lng      REAL            NO                        
geolocation_city     TEXT            NO                        
geolocation_state    TEXT            NO                        

Total rows: 1000163

Table: order_items
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
order_id             TEXT            NO                        
order_item_id        INTEGER         NO                        
product_id           TEXT            NO                        
seller_id            TEXT            NO                        
shipping_limit_date  TEXT            NO                        
price                REAL            NO                        
freight_value        REAL            NO                        

Total rows: 112650

Table: order_payments
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
order_id             TEXT            NO                        
payment_sequential   INTEGER         NO                        
payment_type         TEXT            NO                        
payment_installments INTEGER         NO                        
payment_value        REAL            NO                        

Total rows: 103886

Table: order_reviews
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
review_id            TEXT            NO                        
order_id             TEXT            NO                        
review_score         INTEGER         NO                        
review_comment_title TEXT            NO                        
review_comment_message TEXT            NO                        
review_creation_date TEXT            NO                        
review_answer_timestamp TEXT            NO                        

Total rows: 99224

Table: orders
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
order_id             TEXT            NO                        
customer_id          TEXT            NO                        
order_status         TEXT            NO                        
order_purchase_timestamp TEXT            NO                        
order_approved_at    TEXT            NO                        
order_delivered_carrier_date TEXT            NO                        
order_delivered_customer_date TEXT            NO                        
order_estimated_delivery_date TEXT            NO                        

Total rows: 99441

Table: products
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
product_id           TEXT            NO                        
product_category_name TEXT            NO                        
product_name_lenght  REAL            NO                        
product_description_lenght REAL            NO                        
product_photos_qty   REAL            NO                        
product_weight_g     REAL            NO                        
product_length_cm    REAL            NO                        
product_height_cm    REAL            NO                        
product_width_cm     REAL            NO                        

Total rows: 32951

Table: leads_qualified
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
mql_id               TEXT            NO                        
first_contact_date   TEXT            NO                        
landing_page_id      TEXT            NO                        
origin               TEXT            NO                        

Total rows: 8000

Table: leads_closed
------------------------------------------------------------
Column               Type            Not Null   Default        
------------------------------------------------------------
mql_id               TEXT            NO                        
seller_id            TEXT            NO                        
sdr_id               TEXT            NO                        
sr_id                TEXT            NO                        
won_date             TEXT            NO                        
business_segment     TEXT            NO                        
lead_type            TEXT            NO                        
lead_behaviour_profile TEXT            NO                        
has_company          INTEGER         NO                        
has_gtin             INTEGER         NO                        
average_stock        TEXT            NO                        
business_type        TEXT            NO                        
declared_product_catalog_size REAL            NO                        
declared_monthly_revenue REAL            NO                        

Total rows: 842

============================================================


CREATE TABLE Statements for: olist.sqlite
============================================================

CREATE TABLE "product_category_name_translation" (
"product_category_name" TEXT,
  "product_category_name_english" TEXT
);

CREATE TABLE "sellers" (
"seller_id" TEXT,
  "seller_zip_code_prefix" INTEGER,
  "seller_city" TEXT,
  "seller_state" TEXT
);

CREATE TABLE "customers" (
"customer_id" TEXT,
  "customer_unique_id" TEXT,
  "customer_zip_code_prefix" INTEGER,
  "customer_city" TEXT,
  "customer_state" TEXT
);

CREATE TABLE "geolocation" (
"geolocation_zip_code_prefix" INTEGER,
  "geolocation_lat" REAL,
  "geolocation_lng" REAL,
  "geolocation_city" TEXT,
  "geolocation_state" TEXT
);

CREATE TABLE "order_items" (
"order_id" TEXT,
  "order_item_id" INTEGER,
  "product_id" TEXT,
  "seller_id" TEXT,
  "shipping_limit_date" TEXT,
  "price" REAL,
  "freight_value" REAL
);

CREATE TABLE "order_payments" (
"order_id" TEXT,
  "payment_sequential" INTEGER,
  "payment_type" TEXT,
  "payment_installments" INTEGER,
  "payment_value" REAL
);

CREATE TABLE "order_reviews" (
"review_id" TEXT,
  "order_id" TEXT,
  "review_score" INTEGER,
  "review_comment_title" TEXT,
  "review_comment_message" TEXT,
  "review_creation_date" TEXT,
  "review_answer_timestamp" TEXT
);

CREATE TABLE "orders" (
"order_id" TEXT,
  "customer_id" TEXT,
  "order_status" TEXT,
  "order_purchase_timestamp" TEXT,
  "order_approved_at" TEXT,
  "order_delivered_carrier_date" TEXT,
  "order_delivered_customer_date" TEXT,
  "order_estimated_delivery_date" TEXT
);

CREATE TABLE "products" (
"product_id" TEXT,
  "product_category_name" TEXT,
  "product_name_lenght" REAL,
  "product_description_lenght" REAL,
  "product_photos_qty" REAL,
  "product_weight_g" REAL,
  "product_length_cm" REAL,
  "product_height_cm" REAL,
  "product_width_cm" REAL
);

CREATE TABLE "leads_qualified" (
"mql_id" TEXT,
  "first_contact_date" TEXT,
  "landing_page_id" TEXT,
  "origin" TEXT
);

CREATE TABLE "leads_closed" (
"mql_id" TEXT,
  "seller_id" TEXT,
  "sdr_id" TEXT,
  "sr_id" TEXT,
  "won_date" TEXT,
  "business_segment" TEXT,
  "lead_type" TEXT,
  "lead_behaviour_profile" TEXT,
  "has_company" INTEGER,
  "has_gtin" INTEGER,
  "average_stock" TEXT,
  "business_type" TEXT,
  "declared_product_catalog_size" REAL,
  "declared_monthly_revenue" REAL
);