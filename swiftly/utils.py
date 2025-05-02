import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file_on_filesystem
import json
import pyqrcode
from frappe.utils import get_datetime


@frappe.whitelist()
def get_qr_code(qr_text, scale=5):
    return pyqrcode.create(qr_text).png_as_base64_str(scale=scale, quiet_zone=1)