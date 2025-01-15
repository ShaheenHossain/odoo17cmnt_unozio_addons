/** @odoo-module */
import { registry } from "@web/core/registry"
import { EmailField } from "@web/views/fields/email/email_field"
class EmailValidationWidget extends EmailField {
    setup(){
        super.setup()
    }
    get isValidEmail(){
        let re = /\S+@\S+\.\S+/;
        return re.test(this.props.record.data[this.props.name])
    }
}
EmailValidationWidget.template = "email_validation_widget.EmailFieldValidation"
EmailValidationWidget.supportedTypes = ["char"]
export const emailvalidationwidget = {
    ...EmailField,
    component: EmailValidationWidget,
};
registry.category("fields").add("emailvalidationwidget", emailvalidationwidget);