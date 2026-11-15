-- Database untuk TPK SMARTMU22
-- Jalankan: mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS tpk_smartmu22
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tpk_smartmu22;

-- Tabel dibuat otomatis oleh SQLAlchemy saat aplikasi dijalankan (db.create_all).
-- File ini hanya memastikan database tersedia.