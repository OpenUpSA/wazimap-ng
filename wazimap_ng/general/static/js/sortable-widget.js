function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

django.jQuery(document).ready(function($) {
    $(".sortable" ).sortable({
    	out: function(event, ui) {
    		$parent = ui.item.parent();
            $input = ui.item.parents(".sortable_widget").find("input");
            var reorderedSubindicators = [];
	    	sleep(1000).then(() => { $parent.find("li").each(function(){
	    		reorderedSubindicators.push($(this).data('val'));
                $input.val(JSON.stringify(reorderedSubindicators));
	    	  });
            });
        },
    });

    $(".sortable" ).disableSelection();

} );
