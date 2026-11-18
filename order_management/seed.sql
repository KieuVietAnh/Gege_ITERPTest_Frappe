-- SQL dataset; run through order_management.demo.setup (ORM), not raw INSERTs.
SELECT 'User' AS entity, JSON_OBJECT('email','sale1@example.com','first_name','Nguyễn Minh Anh','role','Order Sales','password','SaleDemo@12345!') AS payload
UNION ALL SELECT 'User', JSON_OBJECT('email','sale2@example.com','first_name','Trần Quốc Huy','role','Order Sales','password','SaleDemo@12345!')
UNION ALL SELECT 'User', JSON_OBJECT('email','kho1@example.com','first_name','Lê Hoàng Nam','role','Order Warehouse','password','KhoDemo@12345!')
UNION ALL SELECT 'User', JSON_OBJECT('email','kho2@example.com','first_name','Phạm Thu Hà','role','Order Warehouse','password','KhoDemo@12345!')
UNION ALL SELECT 'Stock Item', JSON_OBJECT('item_code','KB001','item_name','Bàn phím văn phòng','unit','Cái','default_unit_price',150000,'opening_stock',20)
UNION ALL SELECT 'Stock Item', JSON_OBJECT('item_code','MS001','item_name','Chuột không dây','unit','Cái','default_unit_price',200000,'opening_stock',20)
UNION ALL SELECT 'Stock Item', JSON_OBJECT('item_code','HS001','item_name','Tai nghe USB','unit','Cái','default_unit_price',350000,'opening_stock',20)
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-001','sale','sale1@example.com','warehouse_user','kho1@example.com','customer_name','Văn phòng An Phát','item','KB001','quantity',2,'unit_price',150000,'status','Mới')
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-002','sale','sale2@example.com','warehouse_user','kho2@example.com','customer_name','Trung tâm Sao Mai','item','HS001','quantity',2,'unit_price',350000,'status','Mới')
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-003','sale','sale1@example.com','warehouse_user','kho1@example.com','customer_name','Cửa hàng Minh Anh','item','MS001','quantity',3,'unit_price',200000,'status','Đã giao')
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-004','sale','sale1@example.com','warehouse_user','kho1@example.com','customer_name','Công ty Hòa Bình','item','HS001','quantity',1,'unit_price',350000,'status','Hủy')
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-005','sale','sale2@example.com','warehouse_user','kho2@example.com','customer_name','Văn phòng Thành Công','item','KB001','quantity',1,'unit_price',150000,'status','Đã giao')
UNION ALL SELECT 'Simple Order', JSON_OBJECT('name','DEMO-ORD-006','sale','sale2@example.com','warehouse_user','kho2@example.com','customer_name','Cửa hàng Gia Hưng','item','MS001','quantity',2,'unit_price',200000,'status','Hủy');
