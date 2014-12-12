# -*- coding: utf-8 -*-
##############################################################################
#
#    fiscal_printer
#    Copyright (C) 2014 No author.
#    No email
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import re
from openerp import netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _

_vat = lambda x: x.tax_code_id.parent_id.name == 'IVA'

document_type_map = {
    "DNI":      "D",
    "CUIL":     "L",
    "CUIT":     "T",
    "CPF":      "C",
    "CIB":      "C",
    "CIK":      "C",
    "CIX":      "C",
    "CIW":      "C",
    "CIE":      "C",
    "CIY":      "C",
    "CIM":      "C",
    "CIF":      "C",
    "CIA":      "C",
    "CIJ":      "C",
    "CID":      "C",
    "CIS":      "C",
    "CIG":      "C",
    "CIT":      "C",
    "CIH":      "C",
    "CIU":      "C",
    "CIP":      "C",
    "CIN":      "C",
    "CIQ":      "C",
    "CIL":      "C",
    "CIR":      "C",
    "CIZ":      "C",
    "CIV":      "C",
    "PASS":     "P",
    "LC":       "V",
    "LE":       "E",
};

responsability_map = {
    "IVARI":  "I", # Inscripto, 
    "IVARNI": "N", # No responsable, 
    "RM":     "M", # Monotributista,
    "IVAE":   "E", # Exento,
    "NC":     "U", # No categorizado,
    "CF":     "F", # Consumidor final,
    "RMS":    "T", # Monotributista social,
    "RMTIP":  "P", # Monotributista trabajador independiente promovido.
}

class invoice(osv.osv):
    """"""
    
    _name = 'account.invoice'
    _inherits = {  }
    _inherit = [ 'account.invoice' ]

    def action_fiscal_printer(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        user_obj = self.pool.get('res.users')

        r = {}
        if len(ids) > 1:
            raise osv.except_osv(_(u'Cancelling Validation'),
                                 _(u'Please, validate one ticket at time.'))
            return False

        for inv in self.browse(cr, uid, ids, context):
            if inv.journal_id.use_fiscal_printer:
                journal = inv.journal_id
                ticket={
                    "turist_ticket": False,
                    "debit_note": False,
                    "partner": {
                        "name": inv.partner_id.name,
                        "name_2": "",
                        "address": inv.partner_id.street,
                        "address_2": inv.partner_id.city,
                        "address_3": inv.partner_id.country_id.name,
                        "document_type": document_type_map.get(inv.partner_id.document_type_id.code, "D"),
                        "document_number": inv.partner_id.document_number,
                        "responsability": responsability_map.get(inv.partner_id.responsability_id.code, "F"),
                    },
                    "related_document": (picking_obj.search_read(cr, uid, [('origin','=',inv.origin)], ["name"]) +
                                         [{'name': _("No picking")}])[0]['name'],
                    "related_document_2": inv.origin or "",
                    "turist_check": "",
                    "lines": [ ],
                    "cut_paper": True,
                    "electronic_answer": False,
                    "print_return_attribute": False,
                    "current_account_automatic_pay": False,
                    "print_quantities": True,
                    "tail_no": 1 if inv.user_id.name else 0,
                    "tail_text": _("Saleman: %s") % inv.user_id.name if inv.user_id.name else "",
                    "tail_no_2": 0,
                    "tail_text_2": "",
                    "tail_no_3": 0,
                    "tail_text_3": "",
                }
                for line in inv.invoice_line:
                    ticket["lines"].append({
                        "item_action": "sale_item",
                        "as_gross": False,
                        "send_subtotal": True,
                        "check_item": False,
                        "collect_type": "q",
                        "large_label": "",
                        "first_line_label": "",
                        "description": "",
                        "description_2": "",
                        "description_3": "",
                        "description_4": "",
                        "item_description": line.name,
                        "quantity": line.quantity,
                        "unit_price": line.price_unit,
                        "vat_rate": ([ tax.amount*100 for tax in line.invoice_line_tax_id.filtered(_vat)]+[0.0])[0],
                        "fixed_taxes": 0,
                        "taxes_rate": 0
                    })
                    if line.discount > 0: ticket["lines"].append({
                        "item_action": "discount_item",
                        "as_gross": False,
                        "send_subtotal": True,
                        "check_item": False,
                        "collect_type": "q",
                        "large_label": "",
                        "first_line_label": "",
                        "description": "",
                        "description_2": "",
                        "description_3": "",
                        "description_4": "",
                        "item_description": "%5.2f%%" % line.discount,
                        "quantity": line.quantity,
                        "unit_price": line.price_unit * (line.discount/100.),
                        "vat_rate": ([ tax.amount*100 for tax in line.invoice_line_tax_id.filtered(_vat)]+[0.0])[0],
                        "fixed_taxes": 0,
                        "taxes_rate": 0
                    })

                r = journal.make_fiscal_ticket(ticket)[inv.journal_id.id]

        if r and 'error' not in r:
            import pdb; pdb.set_trace()
            return True
        elif r and 'error' in r:
            raise osv.except_osv(_(u'Cancelling Validation'),
                                 _('Error: %s') % r['error'])
        else:
            raise osv.except_osv(_(u'Cancelling Validation'),
                                 _(u'Unknown error.'))

invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
