/** @odoo-module **/
import publicWidget from '@web/legacy/js/public/public_widget';
import { jsonrpc } from "@web/core/network/rpc_service";

    publicWidget.registry.Scroll = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        start: function () {
            var self = this;
            var lastScrollTop = 0;
            var lastScrollLeft = 0;
            jsonrpc('/website/update_visitor_last_connection', {},
            );
            this._onScroll = function (ev) {
                if(ev.target){
                    var currentScrollTop = ev.target.scrollTop;
                    var currentScrollLeft = ev.target.scrollLeft;
                    var top_difference = Math.abs(currentScrollTop - lastScrollTop);
                    var left_difference = Math.abs(currentScrollLeft - lastScrollLeft);
                    if(top_difference >= 10 || left_difference >= 10){
                        jsonrpc('/website/update_visitor_last_connection', {},
                        );
                        lastScrollTop = currentScrollTop
                        lastScrollLeft = currentScrollLeft
                    }
                }
            };
            window.addEventListener('scroll', this._onScroll, true);
            return this._super.apply(this, arguments);
        },
    });
export default publicWidget.registry.Scroll;
