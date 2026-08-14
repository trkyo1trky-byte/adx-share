-- إنشاء الأدوار الأساسية
INSERT INTO roles (id, name, description) VALUES 
(gen_random_uuid(), 'USER', 'مستخدم عادي'),
(gen_random_uuid(), 'ADMIN', 'مدير النظام');

-- سيتم إضافة المزيد من البيانات لاحقاً في مرحلة Seed Data