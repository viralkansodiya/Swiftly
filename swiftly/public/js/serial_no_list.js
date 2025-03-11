frappe.listview_settings["Serial No"] = {
    onload:(listview)=>{
        listview.page.add_inner_button(__('PDF'), function() {
			let selected_items = listview.get_checked_items();
			if (selected_items.length === 0) {
                frappe.msgprint(__('Please select at least one Serial No.'));
                return;
            }

            let serial_nos = selected_items.map(item => item.name);

            // Call server-side method to generate PDF
            frappe.call({
                method: 'swiftly.swiftly.docevents.serial_no.generate_serial_no_pdf',
                args: { serial_nos: serial_nos },
                callback: function(response) {
                    if (response.message) {
                        window.open(response.message);  // Open the generated PDF
                    }
                }
            });
        });
    },
	add_fields: ["item_code", "warehouse", "warranty_expiry_date", "delivery_document_type"],
	get_indicator: (doc) => {
		if (doc.delivery_document_type) {
			return [__("Delivered"), "green", "delivery_document_type,is,set"];
		} else if (
			doc.warranty_expiry_date &&
			frappe.datetime.get_diff(doc.warranty_expiry_date, frappe.datetime.nowdate()) <= 0
		) {
			return [
				__("Expired"),
				"red",
				"warranty_expiry_date,not in,|warranty_expiry_date,<=,Today|delivery_document_type,is,not set",
			];
		} else if (!doc.warehouse) {
			return [__("Inactive"), "grey", "warehouse,is,not set"];
		} else {
			return [__("Active"), "green", "delivery_document_type,is,not set"];
		}
	},
};
