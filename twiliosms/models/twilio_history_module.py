
from odoo import models, fields, api
import json

class TwilioHistoryModule(models.Model):
    _name = 'twilio.history'
    _description = 'Twilio History'
    _order = 'create_date desc'
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True,readonly=True)

    name = fields.Char(string='Description', required=True,readonly=True)
    model_name = fields.Char(string='Model Name',readonly=True)
    Message = fields.Char(string='Message', required=True,readonly=True)
    Customer_Number = fields.Char(string='Customer Number', required=True,readonly=True)
    From = fields.Char(string='From', required=True,readonly=True)
    Direction = fields.Char(string='Direction',readonly=True)
    Status = fields.Char(string='Status', required=True)
    Channel = fields.Char(string='Channel', required=True,readonly=True)
    WhatsApp_Message = fields.Char(string='WhatsApp Message',readonly=True)
    Sender_Phone = fields.Char(string='Sender Phone',readonly=True)
    Media_URL = fields.Char(string='Media URL',readonly=True)

    timestamp = fields.Datetime(string='Created Time', default=fields.Datetime.now, required=True, readonly=True)


