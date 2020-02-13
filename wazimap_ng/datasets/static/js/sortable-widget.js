(function($) {
    $( "#sortable" ).sortable();
    $( "#sortable" ).disableSelection();


    $("#sortable").on("DOMSubtreeModified", function(){
    	var reorderedSubindicators = [];
    	$("#sortable li").each(function(){
    		reorderedSubindicators.push($(this).data('val'));
    		$('input[name="{{ widget.name }}"]').val(reorderedSubindicators.join(","));
    	});
    });

} )(django.jQuery);