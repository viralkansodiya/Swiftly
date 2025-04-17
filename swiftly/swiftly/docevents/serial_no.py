import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file_on_filesystem
import json
import pyqrcode
from frappe.utils import get_datetime

@frappe.whitelist()
def generate_serial_no_pdf(serial_nos):
    serial_nos = json.loads(serial_nos) if isinstance(serial_nos, str) else serial_nos
    if len(serial_nos) < 21:
        file = generate_qr(serial_nos)
        return file
    else:
        frappe.enqueue(
            generate_qr,
            queue="default",
            serial_nos= serial_nos
        )

def generate_qr(serial_nos):
    
    def get_qr_code(qr_text, scale=5):
        return pyqrcode.create(qr_text).png_as_base64_str(scale=scale, quiet_zone=1)

    html_content = ""
    html_template = """
    <div class="update">
        <table width="100%" style="margin:0;">
            <tr>
                <td align="center" colspan="2">
                    <p><b>Item Code: {item_code}</b></p>
                    <p><b>Serial No: {serial_no}</b></p>
                </td>
            </tr>
            <tr>
                <td align="center" width="40%">
                    <img src="data:image/png;base64,{qr_serial}" alt="QR Serial">
                </td>
                <td align="center" width="60%">
                    <img src="data:image/png;base64,{qr_item}" alt="QR Item">
                </td>
            </tr>
        </table>
    </div>
    <div class="page-break"></div>
    """

    for serial_no in serial_nos:
        doc = frappe.get_doc("Serial No", serial_no)
        html_content += html_template.format(
            item_code=doc.item_code,
            serial_no=doc.name,
            qr_serial=get_qr_code(doc.name, scale=6),
            qr_item=get_qr_code(doc.item_code, scale=5)
        )

    html_content += """
    <style>
        @page {size: 40mm 30mm; margin: 0;}
        .page-break {page-break-after: always;}
        p {font-size: 26px;}
        td {text-align: center; vertical-align: middle; margin: 0;}
        img {display: block; margin: auto;}
    </style>
    """

    pdf_options = {
        "page-width": "140mm",
        "page-height": "110mm",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-right": "0",
        "margin-left": "0",
        "encoding": "UTF-8",
    }
    if len(serial_nos) < 21:
        pdf_content = get_pdf(html_content, options=pdf_options)
        file_doc = save_file_on_filesystem(f"serial_no{str(get_datetime())}.pdf", pdf_content, is_private=0)

        return file_doc.get("file_url")
    
    else:
        content = get_pdf(html_content, options=pdf_options)
        file_doc = save_file_on_filesystem(f"serial_no{str(get_datetime())}.pdf", content=content, is_private=0)
        # doc = frappe.new_doc("File", )
        # file_doc.save(ignore_permissions=True)

        # file_path = frappe.get_site_path("public", file_doc.file_url.lstrip("/"))

        # Read and encode the file content
        # with open(file_path, "rb") as f:
        #     file_content = f.read()

        # encoded_content = base64.b64encode(file_content).decode()

        # Prepare the attachment
        attachment = {
            "fname": file_doc.get("file_name"),
            "fcontent": content
        }

        # Send email
        frappe.sendmail(
            recipients=[frappe.session.user],
            subject="Here is your QR Code PDF",
            message="Please find the attached file.",
            attachments=[attachment],
            now=True
        )
