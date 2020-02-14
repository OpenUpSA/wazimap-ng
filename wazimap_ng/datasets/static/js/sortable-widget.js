django.jQuery(document).ready(function($) {
    $( "#sortable" ).sortable();
    $( "#sortable" ).disableSelection();

    $(document).find("#sortable").on("DOMSubtreeModified", function(){
    	var reorderedSubindicators = [];
    	$(this).find("li").each(function(){
    		reorderedSubindicators.push($(this).data('val'));
    		$(document).find('input[name="subindicators"]').val(reorderedSubindicators.join(","));
    	});
    });

} );