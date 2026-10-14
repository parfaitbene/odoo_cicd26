# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = "account.payment"

    type_operation_id = fields.Many2one('company.caisse.type.operation', 
                                        string="Type d'opération", 
                                        readonly=True, 
                                        domain=lambda self: [('company_id', '=', self.env.company.id)]
                                        )
    imputation_ref = fields.Char('Imputation', readonly=True, required=False)



    def write(self, vals):
        res = super().write(vals)
        self._check_source_journal_balance_ok()

        return res

    def action_post(self):
        super(AccountPayment, self).action_post()

        for record in self:
            if record.type_operation_id and not record.imputation_ref:
                budget_seq = self.env['ir.sequence'].search([('code', '=', 'budget.imputation'), ('company_id', '=', self.env.company.id)], limit=1)
                
                if not budget_seq.exists():
                    raise UserError('Aucune séquence d\'engagement budgétaire trouvée pour %s.'%(self.env.company.name))

                record.imputation_ref = budget_seq._next()
        
            return record

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional list of dictionaries to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :param force_balance: Optional balance.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or []

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %(payment_method)s payment method in the %(journal)s journal.",
                payment_method=self.payment_method_line_id.name, journal=self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = write_off_line_vals or []
        write_off_amount_currency = sum(x['amount_currency'] for x in write_off_line_vals_list)
        write_off_balance = sum(x['balance'] for x in write_off_line_vals_list)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
        else:
            liquidity_amount_currency = 0.0

        if not write_off_line_vals and force_balance is not None:
            sign = 1 if liquidity_amount_currency > 0 else -1
            liquidity_balance = sign * abs(force_balance)
        else:
            liquidity_balance = self.currency_id._convert(
                liquidity_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
            )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        # Compute a default label to set on the journal items.
        liquidity_line_name = ''.join(x[1] for x in self._get_aml_default_display_name_list())
        counterpart_line_name = ''.join(x[1] for x in self._get_aml_default_display_name_list())

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': counterpart_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.type_operation_id and self.type_operation_id.account_id.id or self.destination_account_id.id,
            },
        ]
        return line_vals_list + write_off_line_vals_list

    # -------------------------------------------------------------------------
    # CONSTRAINT METHODS
    # -------------------------------------------------------------------------

    @api.constrains('journal_id', 'destination_journal_id')
    def _check_source_journal_balance_ok(self):
        ''' Prevents negative balance for cash type journals'''
        for pay in self:
            is_source_journal_balance_ok = True
            journal_name = ""

            if pay.payment_type == "outbound" and pay.journal_id.type == "cash":
                if (pay.amount > pay.journal_id.outbound_payment_method_line_ids.payment_account_id.current_balance):
                    is_source_journal_balance_ok = False
                    journal_name = pay.journal_id.name

            if pay.payment_type == "inbound" and pay.destination_journal_id.type == "cash":
                if (pay.amount > pay.destination_journal_id.outbound_payment_method_line_ids.payment_account_id.current_balance):
                    is_source_journal_balance_ok = False
                    journal_name = pay.destination_journal_id.name

            if not is_source_journal_balance_ok:
                raise ValidationError(_('Insufficient funds for cash journal "%s"'%(journal_name)))