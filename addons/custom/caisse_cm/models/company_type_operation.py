# -*- coding:utf-8 -*-
import datetime
import time
import math

from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class CompanyCaisseType(models.Model):
    _name = "company.caisse.type.operation"

    name = fields.Char('Libellé', size=255, required=True)
    account_id = fields.Many2one('account.account', string="Compte", required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    @api.model
    @api.returns('self',
        upgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else self.browse(value),
        downgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else value.ids)
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res =  self._search([('company_id', '=', self.env.company.id)] + args, offset=offset, limit=limit, order=order, count=count)

        return res if count else self.browse(res)