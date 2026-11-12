CREATE DATABASE IF NOT EXISTS koding_smpm22
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE koding_smpm22;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS nilai_detail;
DROP TABLE IF EXISTS nilai;
DROP TABLE IF EXISTS jawaban_siswa;
DROP TABLE IF EXISTS percobaan_ujian;
DROP TABLE IF EXISTS soal;
DROP TABLE IF EXISTS ujian;
DROP TABLE IF EXISTS materi;
DROP TABLE IF EXISTS siswa;
DROP TABLE IF EXISTS kelas;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nama_lengkap VARCHAR(120) NOT NULL,
  role ENUM('guru','siswa') NOT NULL DEFAULT 'siswa',
  aktif TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE kelas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama_kelas VARCHAR(50) NOT NULL UNIQUE,
  tingkat ENUM('7','8','9') NOT NULL DEFAULT '7',
  tahun_ajaran VARCHAR(20) NOT NULL DEFAULT '2026/2027',
  semester ENUM('Ganjil','Genap') NOT NULL DEFAULT 'Ganjil',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE siswa (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  kelas_id INT NOT NULL,
  nis VARCHAR(30) NOT NULL,
  nama_siswa VARCHAR(120) NOT NULL,
  jenis_kelamin ENUM('L','P') NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_kelas_nis (kelas_id, nis),
  CONSTRAINT fk_siswa_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_siswa_kelas FOREIGN KEY (kelas_id) REFERENCES kelas(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE materi (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tingkat ENUM('7','8','9') NOT NULL DEFAULT '7',
  urutan INT NOT NULL DEFAULT 1,
  semester ENUM('Ganjil','Genap') NOT NULL DEFAULT 'Ganjil',
  judul VARCHAR(200) NOT NULL,
  ringkasan TEXT,
  isi_html MEDIUMTEXT NOT NULL,
  contoh_kode TEXT,
  file_nama VARCHAR(255) NULL,
  file_path VARCHAR(500) NULL,
  file_tipe VARCHAR(20) NULL,
  file_ukuran INT NULL,
  aktif TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE ujian (
  id INT AUTO_INCREMENT PRIMARY KEY,
  judul VARCHAR(200) NOT NULL,
  deskripsi TEXT,
  jenis ENUM(
    'latihan',
    'ulangan_harian',
    'sumatif',
    'sts_ganjil',
    'sts_genap',
    'sas'
  ) NOT NULL,
  semester ENUM('Ganjil','Genap') NOT NULL DEFAULT 'Ganjil',
  tingkat ENUM('7','8','9') NOT NULL DEFAULT '7',
  materi_id INT NULL,
  durasi_menit INT NOT NULL DEFAULT 30,
  jumlah_soal INT NOT NULL DEFAULT 10,
  nilai_kkm DECIMAL(5,2) NOT NULL DEFAULT 77.00,
  acak_soal TINYINT(1) NOT NULL DEFAULT 1,
  tampil_pembahasan TINYINT(1) NOT NULL DEFAULT 1,
  aktif TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ujian_materi FOREIGN KEY (materi_id) REFERENCES materi(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE soal (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ujian_id INT NOT NULL,
  nomor INT NOT NULL DEFAULT 1,
  pertanyaan TEXT NOT NULL,
  opsi_a TEXT NOT NULL,
  opsi_b TEXT NOT NULL,
  opsi_c TEXT NOT NULL,
  opsi_d TEXT NOT NULL,
  kunci_jawaban ENUM('A','B','C','D') NOT NULL,
  pembahasan TEXT,
  bobot DECIMAL(5,2) NOT NULL DEFAULT 1.00,
  aktif TINYINT(1) NOT NULL DEFAULT 0,
  CONSTRAINT fk_soal_ujian FOREIGN KEY (ujian_id) REFERENCES ujian(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE percobaan_ujian (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ujian_id INT NOT NULL,
  siswa_id INT NOT NULL,
  mulai_at DATETIME NOT NULL,
  selesai_at DATETIME NULL,
  skor DECIMAL(6,2) NULL,
  status ENUM('berlangsung','selesai') NOT NULL DEFAULT 'berlangsung',
  CONSTRAINT fk_perc_ujian FOREIGN KEY (ujian_id) REFERENCES ujian(id) ON DELETE CASCADE,
  CONSTRAINT fk_perc_siswa FOREIGN KEY (siswa_id) REFERENCES siswa(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE jawaban_siswa (
  id INT AUTO_INCREMENT PRIMARY KEY,
  percobaan_id INT NOT NULL,
  soal_id INT NOT NULL,
  jawaban ENUM('A','B','C','D') NULL,
  benar TINYINT(1) NULL,
  CONSTRAINT fk_jawab_perc FOREIGN KEY (percobaan_id) REFERENCES percobaan_ujian(id) ON DELETE CASCADE,
  CONSTRAINT fk_jawab_soal FOREIGN KEY (soal_id) REFERENCES soal(id) ON DELETE CASCADE,
  UNIQUE KEY uq_jawab (percobaan_id, soal_id)
) ENGINE=InnoDB;

CREATE TABLE nilai (
  id INT AUTO_INCREMENT PRIMARY KEY,
  siswa_id INT NOT NULL,
  ujian_id INT NOT NULL,
  jenis ENUM(
    'latihan',
    'ulangan_harian',
    'sumatif',
    'sts_ganjil',
    'sts_genap',
    'sas'
  ) NOT NULL,
  skor DECIMAL(6,2) NOT NULL,
  percobaan_id INT NULL,
  catatan VARCHAR(255) NULL,
  dinilai_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_nilai_siswa FOREIGN KEY (siswa_id) REFERENCES siswa(id) ON DELETE CASCADE,
  CONSTRAINT fk_nilai_ujian FOREIGN KEY (ujian_id) REFERENCES ujian(id) ON DELETE CASCADE,
  CONSTRAINT fk_nilai_perc FOREIGN KEY (percobaan_id) REFERENCES percobaan_ujian(id) ON DELETE SET NULL,
  UNIQUE KEY uq_nilai_terbaik (siswa_id, ujian_id)
) ENGINE=InnoDB;
