import os
import sqlite3
import hashlib
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, QGroupBox,
    QGridLayout, QCheckBox, QDialog, QFormLayout
)

DB_PATH = "movies.db"