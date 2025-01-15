let parenDoc = window.parent.document;
parenDoc.querySelector('.modal-dialog').style['max-width'] = '740px';
parenDoc.querySelector('.modal-dialog').style['margin'] = 'auto';
parenDoc.querySelector('.modal-dialog footer').style['display'] = 'none';
parenDoc.querySelector('.modal-body').style['overflow'] = 'hidden';

parenDoc.querySelector('.o_act_window .o_form_sheet_bg').style['padding'] = '0px';
parenDoc.querySelector('.o_act_window .o_form_sheet').style['padding'] = '0px';

document.querySelector('iframe').style['border'] = '0px 3px';
document.querySelector('body').style['overflow'] = 'hidden';
document.querySelector('body').style['margin'] = '0px';
