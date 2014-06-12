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

document_type_map = {
    "DNI": "D",
};

responsability_map = {
}

class invoice(osv.osv):
    """"""
    
    _name = 'account.invoice'
    _inherits = {  }
    _inherit = [ 'account.invoice' ]

    def action_fiscal_printer(self, cr, uid, ids, context=None):
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
                        "document_type": document_type_map.get(inv.partner_id.document_type_id.name, "D"),
                        "document_number": inv.partner_id.document_number,
                        "responsability": responsability_map.get(inv.partner_id.responsability_id.name, "F"),
                    },
                    "related_document": "",
                    "related_document_2": "",
                    "turist_check": "",
                    "lines": [ ],
                    "cut_paper": True,
                    "electronic_answer": False,
                    "print_return_attribute": False,
                    "current_account_automatic_pay": False,
                    "print_quantities": True,
                    "tail_no": 0,
                    "tail_text": "",
                    "tail_no_2": 0,
                    "tail_text_2": "",
                    "tail_no_3": 0,
                    "tail_text_3": "",
                }
                for line in inv.invoice_line:
                    ticket["lines"].append({
                        "item_action": "sale_item",
                        "as_gross": False,
                        "send_subtotal": False,
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
                        "vat_rate": 0,
                        "fixed_taxes": 0,
                        "taxes_rate": 0
                    })

                r = journal.make_fiscal_ticket(ticket)[inv.journal_id.id]

        if r:
            return True
        else:
            raise osv.except_osv(_(u'Cancelling Validation'),
                                 _(u'Some error with printer has happening.'))

invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
