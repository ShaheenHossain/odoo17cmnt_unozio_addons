/** @odoo-module **/

	$(document).ready(function() {
		$('.que_ans_links').click(function (e){
			var target = e.currentTarget.classList[1];
			$('.ans_'+target).toggleClass("o_hidden");
			$('.question_'+target).toggleClass("question_color");
		});

	});

