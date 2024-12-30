/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale";


publicWidget.registry.WebsiteSale.include({
    init: function () {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
    },

    start(){
        this._super.apply(this, arguments);

        this.productDetailMain = this.$target[0].querySelector('#product_detail_main');
        var ids = [] 
        
        $(this.target).find('h6.o_wsale_products_item_title a').each(function( i,j ) {
            ids.push($(j).data('oe-id')); 
        });
           
        var self = this;
        this.rpc('/shop/product_item',{'product_ids' : ids}).then(function (result) {
            $(self.target).find('div.show_sale_count').each(function( i,element ) {
                var p_id = $(element).data('oe-id')
                result.total_sales_count.map(function (i,j) {
                    p_id in i ? $(element).find('.show_number_of_counts').html(i[p_id]) : null
                })

                
            });
        });

        var productTemplateId = parseInt($("#product_details").find(".product_template_id").val());

        this.rpc('/shop/product_sale',{'productTemplateId' : productTemplateId}).then(function (result) {
                var totalsales = result.count
                $(".show_number_of_counts_1").html(result['count'])
            });
    },
});
