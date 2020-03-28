django.jQuery(document).ready(function($) {
    $(".sortable" ).sortable({
    	out: function(event, ui) {
    		$parent = ui.item.parent();
            $input = ui.item.parents(".sortable_widget").find("input");
            var reorderedSubindicators = [];
	    	$parent.find("li").each(function(){
	    		console.log($(this).data("val"));
	    		reorderedSubindicators.push($(this).data('val'));
	    		console.log(reorderedSubindicators.join(","));
	    		$input.val(reorderedSubindicators.join(","));
	    	});
        },
    });

    $(".sortable" ).disableSelection();

} );