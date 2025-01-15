# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from datetime import datetime
from odoo import fields
import logging
from datetime import datetime
import pytz
# Get the logger instance for this module
_logger = logging.getLogger(__name__)

class SAASAPIS(http.Controller):
    
    modelNameMap = {
        'res.partner': 'Contacts',
        'crm.lead': 'Leads',
        'res.users': 'Users',
        'twilio.history': 'TwilioHistory',
        'calendly.history': 'CalendlyHistory',
    }

    modelStringNameMap = {
        'Contacts': 'res.partner',
        "Leads": 'crm.lead',
        "Users": 'res.users',
        "TwilioHistory": 'twilio.history',
        "CalendlyHistory": 'calendly.history'
    }
    
    def _filter_fields_by_type(self, record):
        allowed_types = (str, int, float, bool, list, dict)  # Add other allowed types as needed
        filtered_record = {}
        for key, value in record.items():
            if isinstance(value, allowed_types):
                filtered_record[key] = value
        return filtered_record

    def checkAuthorization(self):
        access_token = request.httprequest.headers.get('Authorization')
        if not access_token:
            return json.dumps({'status': 'error', 'message': 'Key not found'})

        if access_token.startswith('Bearer '):
            access_token = access_token[7:]

        user_id = request.env["res.users.apikeys"]._check_credentials(scope='odoo.plugin.outlook', key=access_token)
        if not user_id:
            return False
        user = request.env['res.users'].sudo().browse(int(user_id))
        if not user:
            return False
        return True
    
    @http.route('/ulgebra-odoo/records', type='http', auth='public', methods=['GET'])
    def getRecords(self, **kwargs):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })
        partner_ids = kwargs.get('ids')
        partner_ids = partner_ids.split(',')
        
        partner_ids = [int(num_str) for num_str in partner_ids]
        if not partner_ids or not isinstance(partner_ids, list):
            return {'error': 'Invalid input. Expected a list of partner IDs.'}
        
        model_string_name = kwargs.get('model')
        model_name = self.modelStringNameMap[model_string_name]
        partners = request.env[model_name].sudo().browse(partner_ids)
        partner_data = partners.read()
        # Filter fields by data type
        filtered_partner_data = [self._filter_fields_by_type(record) for record in partner_data]

        # Serialize to JSON
        
        response = {
            'data': filtered_partner_data
        }
        return json.dumps(response)

   

    @http.route('/ulgebra-odoo/home', type='http', auth='public', methods=['GET'])
    def twiliosmsPage(self, **kwargs):
        entityIds = request.params.get('ids')
        model = request.params.get('model')
        appCode = request.params.get('appCode')
        model_string_name = self.modelNameMap[model]
        server_url = request.httprequest.url_root
        server_domain = server_url.replace('https://','').replace('http://','').replace('/','')

        parentHtmlPage = f"""
                             <iframe id='app-iframe' src='https://sms.ulgebra.com/app?appCode={appCode}&disableSAASSdk=true&force-ui-view=MESSAGE_FORM&entityId={entityIds}&module={model_string_name}&api_domain={server_domain}' style='width: 100%;height: 100%;border:0px'> </iframe> </div>
                             <script src="/ulgebra-odoo/static/src/js/iframe-ui.js"></script>
                            """
        return parentHtmlPage

    @http.route('/ulgebra-odoo/users/me', type='http', auth='public', methods=['GET'], csrf=False)
    def get_current_user(self):
        
        access_token = request.httprequest.headers.get('Authorization')
        if not access_token:
            return json.dumps({'status': 'error', 'message': 'Key not found'})

        if access_token.startswith('Bearer '):
            access_token = access_token[7:]
        print(access_token)
        user_id = request.env["res.users.apikeys"]._check_credentials(scope='odoo.plugin.outlook', key=access_token) or False
        if not user_id:
            return json.dumps({'status': 'error', 'message': 'User not found'})
        
        user = request.env['res.users'].sudo().browse(int(user_id))
       
        user_data = self._filter_fields_by_type(user.read()[0])
       
        return json.dumps({'status': 'success', 'user': user_data, 'test': 1})


    @http.route('/ulgebra-odoo/settings/fields', type='http', auth='public', methods=['GET'])
    def getFields(self, **kwargs):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })
        model_string_name = kwargs.get('model')
        model_name = self.modelStringNameMap[model_string_name]
        if not model_name:
            return {'error': 'Invalid input. Expected a model name.'}

        try:
            # Get the model
            model = request.env[model_name]

            # Get the fields metadata
            fields_metadata = model.fields_get()

            # Allowed field types
            allowed_types = {'char', 'integer', 'boolean', 'float'}

            # Filter fields by type
            filtered_fields_metadata = {
                field_name: field_info
                for field_name, field_info in fields_metadata.items()
                if field_info['type'] in allowed_types
            }

            # Serialize to JSON
            json_fields_metadata = (filtered_fields_metadata)
            response = {
                'fields': [json_fields_metadata]
            }
            return json.dumps(response)
        except Exception as e:
            return {'error': str(e)}


    @http.route('/ulgebra-odoo/instance', type='http', auth='public', methods=['GET'], csrf=False)
    def get_instance_uuid(self):
        # Get the database UUID
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })
        db_uuid = request.env['ir.config_parameter'].sudo().get_param('database.uuid')
        return json.dumps({'status': 'success', 'org' : { 'instance_uuid': db_uuid}})

    @http.route('/ulgebra-odoo/users', type='http', auth='public', methods=['GET'], csrf=False)
    def get_all_users(self,**kwargs):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })
        # Search for all user records
        limit = kwargs.get('limit') or 0
        offset = kwargs.get('offset') or 0
        limit = int(limit)
        offset = int(offset)
        users = request.env['res.users'].sudo().search([],limit=limit, offset=offset)

        # Prepare the data to return
        user_data = []
        for user in users:
            user_info = {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'email': user.email,
                'phone': user.phone,
                'is_admin': user._is_admin(),
                'company_id': user.company_id.id,
                'company_name': user.company_id.name,
                'create_date': user.create_date.strftime('%Y-%m-%d %H:%M:%S') if user.create_date else None,
                'write_date': user.write_date.strftime('%Y-%m-%d %H:%M:%S') if user.write_date else None
            }
            user_data.append(user_info)

        return json.dumps({'status': 'success', 'users': user_data, 'meta' : {'nextOffset': str(offset + limit) }})

   
    @http.route('/ulgebra-odoo/create_history_log', type='http', auth='public', methods=['POST'], csrf=False)
    def create_history_record(self, **kwargs):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })
        
        model_string_name = request.params.get('model_name')
        model = self.modelStringNameMap[model_string_name]
        access_token = request.httprequest.headers.get('Authorization')
        if not access_token:
            return json.dumps({'status': 'error', 'message': 'Key not found'})

        if access_token.startswith('Bearer '):
            access_token = access_token[7:]

        user_id = request.env["res.users.apikeys"]._check_credentials(scope='odoo.plugin.outlook', key=access_token)
        
        data = kwargs
        
        name = data.get('name')
        history = {}

        if(model == 'twilio.history'):
            Message = data.get('Message')
            Customer_Number = data.get('Customer_Number') or ""
            From = data.get('From') or ""
            Direction = data.get('Direction') or ""
            Status =  data.get('Status') or ""
            Channel = data.get('Channel') or ""
            WhatsApp_Message =  data.get('WhatsApp_Message') or ""
            Sender_Phone = data.get('Sender_Phone') or ""
            Media_URL =  data.get('Media_URL') or ""
            model_string_name =  data.get('model_name') or ""

            # Create the history log record
            history = request.env[model].sudo().create({
                'name': name,
                'model_name': model_string_name,
                'Message': Message,
                'Customer_Number': Customer_Number,
                'From': From,
                'user_id': user_id,
                'Status': Status,
                'Direction': Direction,
                'Channel': Channel,
                'WhatsApp_Message': WhatsApp_Message,
                'Sender_Phone': Sender_Phone,
                'Media_URL': Media_URL,
                'timestamp': datetime.utcnow(),
            })

        if(model == 'calendly.history'):
            Start_Time = data.get('Start_Time') or ""
            End_Time = data.get('End_Time') or ""
            Status = data.get('Status') or ""
            Invitee_Email =  data.get('Invitee_Email') or ""
            Assignee_Email = data.get('Assignee_Email') or ""
            Guest_Emails =  data.get('Guest_Emails') or ""
            Contact_Number =  data.get('Contact_Number') or ""
            Invitee_Timezone =  data.get('Invitee_Timezone') or ""
            Event_Type =  data.get('Event_Type') or ""
            Location =  data.get('Location') or ""
            Cancel_URL =  data.get('Cancel_URL') or ""
            Reschedule_URL =  data.get('Reschedule_URL') or ""

            createData = {
                'name': name,
                'model_name': model_string_name,
                'Start_Time': Start_Time,
                'End_Time': End_Time,
                'Assignee_Email': Assignee_Email,
                'Invitee_Email': Invitee_Email,
                'user_id': user_id,
                'Guest_Emails': Guest_Emails,
                'Contact_Number': Contact_Number,
                'Invitee_Timezone': Invitee_Timezone,
                'Event_Type': Event_Type,
                'Location': Location,
                'Cancel_URL': Cancel_URL,
                'Reschedule_URL': Reschedule_URL,
                'timestamp': datetime.utcnow(),
            }
            # print(json.dumps(createData))
            # Create the history log record
            history = request.env[model].sudo().create(createData)

        return json.dumps({'status': 'success', 'message': 'History log created successfully', 'data': {
            'id': history.id
        }})

    @http.route('/ulgebra-odoo/active_models', type='http', auth='public', methods=['GET'], csrf=False)
    def get_active_models(self):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })

        # Fetch all active models
        models = request.env['ir.model'].sudo().search([('state', '=', 'base')])

        # Extract model information
        model_data = []
        for model in models:
            model_data.append({
                'model': model.model,
                'name': model.name,
                'info': model.info,
            })

        return json.dumps({'status': 'success', 'models': model_data})


    @http.route('/ulgebra-odoo/search', type='http', auth='public', methods=['GET'], csrf=False)
    def search_records(self, **kwargs):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })

        # Fetch all active models
        model_string_name = kwargs.get('model')
        model_name = self.modelStringNameMap[model_string_name]
        phone = (kwargs.get('phone') or "")
        phone = str(phone)

        email = (kwargs.get('email_from') or "") if (model_name == 'crm.lead') else (kwargs.get('email') or "") 
        email = str(email)

        name = (kwargs.get('name') or "")
        name = str(name)
        
        if not model_name:
            return json.dumps({'status': 'error', 'message': 'Missing model name'})

        # Search for records in the specified model
        partners = {}
        try:
            if email and len(email) > 0:
                partners = request.env[model_name].sudo().search([('email', '=', email)])
            if name and len(name) > 0:
                if model_name == "crm.lead":
                    partners = request.env[model_name].sudo().search([('contact_name', 'ilike', name)])
                else:
                    partners = request.env[model_name].sudo().search([('name', 'ilike', name)])
                
            if phone and len(phone) > 0:
                partners = request.env[model_name].sudo().search(['|',('phone', 'ilike', phone),('mobile', 'ilike', phone)])
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

        # Prepare the result data
        partner_data = []
        if partners:
            partner_data = partners.read()

        # Filter fields by data type
        filtered_partner_data = [self._filter_fields_by_type(record) for record in partner_data]

        return json.dumps({'status': 'success', 'data': filtered_partner_data })


    @http.route('/ulgebra-odoo/create_record', type='http', auth='public', methods=['POST'], csrf=False)
    def create_record(self, **kwargs):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })

        model_string_name = request.params.get('model')
        model_name = self.modelStringNameMap[model_string_name]

        all_fields = {}
        
        for key, value in kwargs.items():
            if key != 'model':
                all_fields[key] = value

        record = request.env[model_name].sudo().create(all_fields)

        return json.dumps({'status': 'success', 'message': 'Record log created successfully', 'data': {
            'id': record.id,
        },
        'record_data': {
                'id': record.id,
                'name': record.name,
                'phone': record.phone,
        }})
    


    @http.route('/ulgebra-odoo/Events', type='http', auth='public', methods=['POST'], csrf=False)
    def create_event(self, **kwargs):
        if not self.checkAuthorization():
            return json.dumps( {'message': "UnAuthorized", 'error': True })
        name = kwargs.get('name')
        assignee = kwargs.get('contact_name') or ''
        email = kwargs.get('email')
        timezone = kwargs.get('timezone')
        phone = kwargs.get('phone') or ''
        date_begin = (kwargs.get('date_begin'))
        date_end = (kwargs.get('date_end'))
        contact_id = kwargs.get('contact_id')
        date_begin = datetime.strptime(date_begin[:-1], '%Y-%m-%dT%H:%M:%S.%f')
        date_end = datetime.strptime(date_end[:-1], '%Y-%m-%dT%H:%M:%S.%f')

        event = request.env['event.event'].sudo().create({
            'name': name,
            'date_begin': date_begin,
            'date_end': date_end,
            'event_mail_ids': False,
            'date_tz': timezone,
        })

        assigneeData = {
            'name': assignee,
            'event_id': event.id,
            'email': email,
            'phone': phone
        }
        
        if(contact_id):
            assigneeData['partner_id'] = contact_id

        registration = request.env['event.registration'].sudo().create({
            'name': assignee,
            'event_id': event.id,
            'email': email,
            'phone': phone
        })

        return json.dumps({'status': 'success', 'message': 'Event created successfully', 'data': { 'id': registration.id, }})
        