-- Seed dataset for MariaDB/Frappe. Run through order_management.demo.setup,
-- not directly as INSERTs: User passwords/roles and stock must use Frappe ORM.
SELECT 'User' AS entity, JSON_OBJECT('email','sale1@example.com','first_name','Sale 1','role','Order Sales','password','SaleDemo@12345!') AS payload
UNION ALL SELECT 'User', JSON_OBJECT('email','sale2@example.com','first_name','Sale 2','role','Order Sales','password','SaleDemo@12345!')
UNION ALL SELECT 'User', JSON_OBJECT('email','kho1@example.com','first_name','Kho 1','role','Order Warehouse','password','KhoDemo@12345!')
UNION ALL SELECT 'User', JSON_OBJECT('email','kho2@example.com','first_name','Kho 2','role','Order Warehouse','password','KhoDemo@12345!')
UNION ALL SELECT 'Stock Item', JSON_OBJECT('item_code','KB001','item_name','Bàn phím','unit','Cái','default_unit_price',150000,'opening_stock',20)
UNION ALL SELECT 'Stock Item', JSON_OBJECT('item_code','MS001','item_name','Chuột','unit','Cái','default_unit_price',200000,'opening_stock',20)
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-001','sale','sale1@example.com','customer_name','Khách mẫu Sale 1','item','KB001','quantity',2,'unit_price',150000,'warehouse_user','kho1@example.com')
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-002','sale','sale2@example.com','customer_name','Khách mẫu Sale 2','item','MS001','quantity',1,'unit_price',200000,'warehouse_user','kho2@example.com');
