import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file, save_file_on_filesystem
import json

@frappe.whitelist()
def generate_serial_no_pdf(serial_nos):
    serial_nos = json.loads(serial_nos) if isinstance(serial_nos, str) else serial_nos
    # Fetch print format HTML
    
    html_print_format = """
                        
                    <div class="update">
                       
                        <br>
                        <table width="100%"  style="margin:0;">
                            <tr>
                                <td align="center"  style="margin:0;" colspan="2">
                                    <p style="padding-bottom:0px; !important;"><b>Item Code: {0}</b></p>
                                    <p><b>Serial No: {1}</b></p>
                                </td>
                            </tr>
                            <tr>
                                <td align="center" style="margin:0px">
                                    <span style="text-align:center;" align="center"><img alt="" src="data:image/png;base64,{2}"></span>
                                </td>
                                <td align="center" style="margin:0px">
                                    <span style="text-align:center;" align="center"><img alt="" src="data:image/png;base64,{3}"></span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div class="page-break"></div>

    """
    html_content = ""
    for serial_no in serial_nos:
        doc = frappe.get_doc("Serial No", serial_no)
        html_print_format = html_print_format.format(
            doc.item_code, doc.name, get_qr_code(doc.name, scale=6), get_qr_code(doc.item_code, scale=5)
        )
        # Pass the full document instead of separate fields
        final_content = frappe.render_template(html_print_format, {"doc": {'name':doc.name, "item_code":doc.item_code }}) 
        html_content += final_content
        html_content += "<div class='page-break'></div>"

    # Convert HTML to PDF
        html_content        +="""
                <style>
                    @page {size: 40mm 30mm; margin: 0;
                    }

                    .print-format td {
                        padding : 0px !important;
                    }
                    
                    .page-break {
                        page-break-after: always;
                    }
                    
                    p{
                        font-size:26px;
                    }
                        body:last-child .print-format td img {
                        width: 60% !important;
                    }
                    td {
                        text-align: center !important; 
                        vertical-align: middle; 
                    }
                    td img {
                        display: block;
                        margin: auto; 
                    }


                    </style>"""
    pdf_options = {
        "page-width": "150mm",
        "page-height": "130mm",
        "margin-top": "0mm",
        "margin-bottom": "0mm",
        "margin-right": "0mm",
        "margin-left": "0mm",
        "encoding": "UTF-8",
        "orientation": "Portrait"  
    }
    pdf_content = get_pdf(html_content, options=pdf_options)

    file_doc = save_file_on_filesystem("Selected_Serial_Nos.pdf", pdf_content, is_private=0)
    
    return file_doc.get("file_url")  

import pyqrcode
def get_qr_code(qr_text, scale=5):
    return pyqrcode.create(qr_text).png_as_base64_str(scale=scale, quiet_zone=1)
