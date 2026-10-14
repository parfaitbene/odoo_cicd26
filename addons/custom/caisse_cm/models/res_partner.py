# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import timedelta


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def action_create_customer_account(self):
        for record in self:
            if record._check_customer_account_exists():
                raise UserError(_(u'Ce contact possède déjà un compte client dans le plan comptable.'))
            else:
                partner_seq = None            
                partner_seq = self.env['ir.sequence'].search([('code', '=', 'customer.account.seq'), ('company_id', '=', self.env.company.id)], limit=1)
                
                if not partner_seq.exists():
                    raise UserError(_(u'Aucune séquence de création de compte client trouvée pour %s.')%(self.env.company.name))

                try:
                    account_data = {
                        'code': partner_seq._next(),
                        'name': _('Client - ') + record.name,
                        'account_type': "asset_receivable",
                        'reconcile': True
                    }
                    partner_account = self.env['account.account'].create(account_data)
                    record.property_account_receivable_id = partner_account
                except:
                    partner_seq._next_do()
                

    def action_create_supplier_account(self):
        for record in self:
            if record._check_supplier_account_exists():
                raise UserError(_(u'Ce contact possède déjà un compte fournisseur dans le plan comptable.'))
            else:
                partner_seq = None
                partner_seq = self.env['ir.sequence'].search([('code', '=', 'supplier.account.seq'), ('company_id', '=', self.env.company.id)], limit=1)
                
                if not partner_seq.exists():
                    raise UserError(_(u'Aucune séquence de création de compte fournisseur trouvée pour %s.')%(self.env.company.name))

                try:
                    account_data = {
                        'code': partner_seq._next(),
                        'name': _('Fournisseur - ') + record.name,
                        'account_type': "liability_payable",
                        'reconcile': True
                    }
                    partner_account = self.env['account.account'].create(account_data)
                    record.property_account_payable_id = partner_account
                except:
                    partner_seq._next_do()

    def _check_customer_account_exists(self):
        for record in self:
            customer_account = self.env['account.account'].with_company(self.env.company).search([('name', 'ilike', record.name), ('code', 'ilike', '411')])

            if len(customer_account):
                return True
            else:
                return False
            
    def _check_supplier_account_exists(self):
        for record in self:
            supplier_account = self.env['account.account'].with_company(self.env.company).search([('name', 'ilike', record.name), ('code', 'ilike', '401')])

            if len(supplier_account):
                return True
            else:
                return False
