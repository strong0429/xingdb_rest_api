-- SQLite
DELETE FROM dbs_goods_category_l1;
DELETE FROM dbs_goods_category_l2;

INSERT INTO dbs_goods_category_l1 VALUES (1,'影音.通信.数码');
INSERT INTO dbs_goods_category_l1 VALUES (2,'食品.酒类.生鲜');
INSERT INTO dbs_goods_category_l1 VALUES (3,'图书.文具.娱乐');


INSERT INTO dbs_goods_category_l2 VALUES (1,'手机通信',1);
INSERT INTO dbs_goods_category_l2 VALUES (2,'手机配件',1);
INSERT INTO dbs_goods_category_l2 VALUES (3,'摄影摄像',1);
INSERT INTO dbs_goods_category_l2 VALUES (4,'影音娱乐',1);
INSERT INTO dbs_goods_category_l2 VALUES (5,'智能设备',1);

INSERT INTO dbs_goods_category_l2 VALUES (6,'新鲜水果',2);
INSERT INTO dbs_goods_category_l2 VALUES (7,'中外烟酒',2);
INSERT INTO dbs_goods_category_l2 VALUES (8,'粮油调味',2);
INSERT INTO dbs_goods_category_l2 VALUES (9,'饮料冲调',2);
INSERT INTO dbs_goods_category_l2 VALUES (10,'休闲食品',2);

INSERT INTO dbs_goods_category_l2 VALUES (11,'文学',3);
INSERT INTO dbs_goods_category_l2 VALUES (12,'艺术',3);
INSERT INTO dbs_goods_category_l2 VALUES (13,'杂志期刊',3);
INSERT INTO dbs_goods_category_l2 VALUES (14,'文娱音像',3);
INSERT INTO dbs_goods_category_l2 VALUES (15,'科学技术',3);