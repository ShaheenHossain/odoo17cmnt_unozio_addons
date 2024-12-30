/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.Loyalty = publicWidget.Widget.extend({
        selector: ".input-group, #reward_apply, .cart_line, .oe_cart",
         events: {
            "focusout #email": "email_focusout",
            "click #redeem_reward": "click_redeem_reward",
        },
        init(parent, options) {
            this._super(parent, options);
            this.rpc = this.bindService("rpc");
            this.orm = this.bindService("orm");
        },

        start: function () {
            var self = this
            this._super.apply(this, arguments);
            var applied_reward = $('#applied_reward');
            var applied_reward_counter;

            applied_reward.popover({
                trigger: 'auto',
                animation: true,
                html: true,
                title: function () {
                    return ("Applied Reward");
                },
                container: 'body',
                placement: 'auto',
                template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body">AAA</div></div>'
            }).on("mouseenter", function () {
                var self = this;
                clearTimeout(applied_reward_counter);
                applied_reward.not(self).popover('hide');
                applied_reward_counter = setTimeout(function () {
                    if ($(self).is(':hover') && !$(".mycart-popover:visible").length) {
                        $.get("/shop/applied_reward", {'type': 'popover'})
                            .then(function (data) {
                                const popover = Popover.getInstance(self);
                                popover._config.content = data;
                                $(self).popover("show");
                                $(".popover").on("mouseleave", function () {
                                    $(self).trigger('mouseleave');
                                });
                            });
                    }
                }, 100);

            }).on("mouseleave", function () {
                var self = this;
                setTimeout(function () {
                    if (!$(".popover:hover").length) {
                        if (!$(self).is(':hover')) {
                            $(self).popover('hide');
                        }
                    }
                }, 1000);
            }).on('shown.bs.popover', function(e) {
                var current_popover = '#' + $(e.target).attr('aria-describedby');
                var $cur_pop = $(current_popover);
                $cur_pop.find('.cancel_applied_reward').click(function(){
                    var csrf = $(this).attr('data-csrf');
                    var redeem_id = $(this).attr('data-id');
                    var amount = $(this).attr('data-amount');
                    self.rpc("/cancel_reward", {'csrf':csrf, 'redeem_id': redeem_id, 'amount': amount})
                    .then(function (data) {
                        if (data) {
                            location.replace('/shop/payment');
                        }
                    });
                });
            });
        },


        email_focusout: function (ev) {
            var email = $("#email").val()
             this.orm.call("res.partner", "referral_partner", [
                false,$("#email").val(),
            ])
        },

        click_redeem_reward: function (ev) {
                this.rpc("/redeerm/reward", {})
                .then(function (data) {
                    location.reload();
                });
        },
    });
