import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "smartmu-smpm22-ubah-di-produksi")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
SMARTMU_DATABASE = os.getenv("SMARTMU_DATABASE", "smartmu")

# Nama database bawaan tiap modul. Jangan disatukan jadi satu skema:
# tabel users, kelas, dan siswa bentrok antara eRapor dan Tahfidz.
PRESENSI_DATABASE = os.getenv("PRESENSI_DATABASE", "db_presensi_smpm22")
ERAPOR_DATABASE = os.getenv("MYSQL_DATABASE", "erapor_smamduma")
TAHFIDZ_DATABASE = os.getenv("MYSQL_DB", "tahfidz_smpm22")
INVENTARIS_DATABASE = os.getenv("INVENTARIS_DATABASE", "inventaris_smpm22")
