# -*- coding: utf-8 -*-

from openerp import netsvc
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)
_schema = logging.getLogger(__name__ + '.schema')

class account_journal(osv.osv):
    def _get_fp_items_generated(self, cr, uid, ids, fields_name, arg, context=None):
        context = context or {}
        r = {}
        for jou in self.browse(cr, uid, ids, context):
            fp = jou.fiscal_printer_id
            res = fp.get_counters() if fp else False
            if res and res[fp.id]:
                if jou.journal_class_id.afip_code == 1: 
                    r[jou.id] = res[fp.id]['last_a_sale_document_completed']
                elif jou.journal_class_id.afip_code in [ 6, 11 ]:
                    r[jou.id] = res[fp.id]['last_b_sale_document_completed']
                else:
                    r[jou.id] = False
            else:
                r[jou.id] = False
        return r

    _name = "account.journal"

    _inherit = ["account.journal", "fpoc.user"]

    _columns = {
        'use_fiscal_printer': fields.boolean('Associated to a fiscal printer'),

        'fiscal_printer_items_generated': fields.function(_get_fp_items_generated, type='integer', string='Number of Invoices Generated',method=True, 
                            help="Check how many invoices was generated in the printer.", readonly=True),
    }
 
account_journal()

