from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe.utils import flt,today, get_link_to_form
from frappe import _


def validate(doc, method):
	# fix variable rate
	set_po_item_rate(doc)


def set_po_item_rate(doc):
	if doc.items:
		for item in doc.items:
			if item.po_detail:
				rate = frappe.db.get_value('Purchase Order Item', item.po_detail, 'rate')
				if item.maintain_fix_rate == 1 and rate != item.rate:
					frappe.throw('Not allowed to change the rate for <b>Row {0}</b> as <b>Maintain Fix Rate</b> is checked on the purchase order {1}'.format(item.idx, get_link_to_form('Purchase Order', item.purchase_order)))

def validate_supplier_invoice_no(self):
		if self.bill_date:
			if getdate(self.bill_date) > getdate(self.posting_date):
				frappe.throw(_("Supplier Invoice Date cannot be greater than Posting Date"))

		if self.bill_no:
			if cint(frappe.db.get_single_value("Accounts Settings", "check_supplier_invoice_uniqueness")):
				fiscal_year = get_fiscal_year(self.posting_date, company=self.company, as_dict=True)

				pi = frappe.db.sql('''select name from `tabPurchase Invoice`
					where
						bill_no = %(bill_no)s
						and supplier = %(supplier)s
						and name != %(name)s
						and docstatus < 2
						and is_rate_differences__credit_note = 0
						and posting_date between %(year_start_date)s and %(year_end_date)s''', {
							"bill_no": self.bill_no,
							"supplier": self.supplier,
							"name": self.name,
							"year_start_date": fiscal_year.year_start_date,
							"year_end_date": fiscal_year.year_end_date
						})

				if pi:
					pi = pi[0][0]
					frappe.throw(_("Supplier Invoice No exists in Purchase Invoice {0}").format(pi))