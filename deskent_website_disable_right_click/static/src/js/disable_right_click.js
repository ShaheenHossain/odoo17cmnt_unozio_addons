/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";
    $(document).ready(function () {
        jsonrpc("/web/dataset/call_kw", {
            model: 'ir.config_parameter',
            method: 'get_param',
            args: ['website.disable_right_click'],
            kwargs: {},
        })
        .then(function (disable_right_click) {
            if (disable_right_click === 'True') {
                jsonrpc("/web/dataset/call_kw", {
                    model: 'ir.config_parameter',
                    method: 'get_param',
                    args: ['website.show_popup_message'],
                    kwargs: {},
                })
                .then(function (show_popup_message) {
                    if (show_popup_message === 'True') {
                        $("html").on("contextmenu", function (e) {
                            Swal.fire({
                              icon: "error",
                              title: "Oops...",
                              text: "Right click is disabled",
                            });
                            return false;
                        });
                    } else {
                        $("html").on("contextmenu", function (e) {
                            return false;
                        });
                    }
                });
            }
        });
    }); 