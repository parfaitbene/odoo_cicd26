# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import timedelta


class Product(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    def action_create_income_account(self):
        for record in self:
            if record._check_product_income_account_exists():
                raise UserError(_(u'Cet enregistrement possède déjà un compte produit dans le plan comptable.'))
            else:
                product_seq = None            
                product_seq = self.env['ir.sequence'].search([('code', '=', 'product.income.account.seq'), ('company_id', '=', self.env.company.id)], limit=1)
                
                if not product_seq.exists():
                    raise UserError(_(u'Aucune séquence de création de compte produit trouvée pour %s.')%(self.env.company.name))

                try:
                    account_data = {
                        'code': product_seq._next(),
                        'name': _('Vente - ') + record.name,
                        'account_type': "income",
                    }
                    partner_account = self.env['account.account'].create(account_data)
                    record.property_account_income_id = partner_account
                except:
                    product_seq._next_do()
                

    def action_create_expense_account(self):
        for record in self:
            if record._check_product_expense_account_exists():
                raise UserError(_(u'Cet enregistrement possède déjà un compte de charge dans le plan comptable.'))
            else:
                product_seq = None
                product_seq = self.env['ir.sequence'].search([('code', '=', 'product.expense.account.seq'), ('company_id', '=', self.env.company.id)], limit=1)
                
                if not product_seq.exists():
                    raise UserError(_(u'Aucune séquence de création de compte dépense trouvée pour %s.')%(self.env.company.name))

                try:
                    account_data = {
                        'code': product_seq._next(),
                        'name': _('Achat - ') + record.name,
                        'account_type': "expense",
                    }
                    partner_account = self.env['account.account'].create(account_data)
                    record.property_account_expense_id = partner_account
                except:
                    product_seq._next_do()

    def _check_product_income_account_exists(self):
        for record in self:
            customer_account = self.env['account.account'].with_company(self.env.company).search([('name', 'ilike', record.name), ('code', 'ilike', '7011')])

            if len(customer_account):
                return True
            else:
                return False
            
    def _check_product_expense_account_exists(self):
        for record in self:
            supplier_account = self.env['account.account'].with_company(self.env.company).search([('name', 'ilike', record.name), ('code', 'ilike', '6011')])

            if len(supplier_account):
                return True
            else:
                return False