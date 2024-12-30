/** @odoo-module **/


import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from '@web/core/network/rpc_service';
import { useService } from "@web/core/utils/hooks";

	$(document).ready(function() {
		var oe_website_sale = this;
		
		var $giftwrap = $("#row_data");

		$('.item_image').each(function(){

			$('.raghav').removeClass('raghav');
            $("#myPack").find(".item_image").first().addClass('raghav');
			$(this).on('click',function () {
				if ( $(this).hasClass('raghav') )
				{
					$('.raghav').removeClass('raghav');
				}
				else{
					$('.raghav').removeClass('raghav');
					$(this).addClass('raghav');
				}
			});
		});

		$('#giftwrapbutton').on('click', function() {
				var self = this;
				var notes = $("#notes").val();
				var product = $(".raghav").data('id');
				
				if (product){
					jsonrpc('/shop/cart/giftwrap', {
						'notes': notes,
						'product':product,
					}).then(function (notes) {
						// console.log("---------orm-------",notes)
						location.reload();
					});
				}
				else{					
					alert("Pleas Select Gift Wrap Product..!");

				}				
				
			});

			
		
		
	});
