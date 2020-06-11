django.jQuery(document).ready(function($) {
    $(function () {
       loadHeirarchyHelpText()
        $("#id_geography_hierarchy").on('change', function() {
            loadHeirarchyHelpText();
        });
    });

    function loadHeirarchyHelpText() {
        var geographyHierarchyID = $(document).find("#id_geography_hierarchy").val();
        var $help_div = $(document).find(".field-geography_hierarchy .help");

        if (geographyHierarchyID) {
            var url = '/api/v1/geography/hierarchies/' + geographyHierarchyID + "/";
            $.ajax({
                url: url,
                success: function(data) {
                    var $help_div = $(document).find(".field-geography_hierarchy .help");
                    if ($help_div.length){
                        $help_div.empty();
                    }else{
                        $(document).find(".field-geography_hierarchy").append("<div class='help'></div>");
                        $help_div = $(document).find(".field-geography_hierarchy .help");
                    }
                    let description = data.description.length ? data.description : "Description not Provided for this hierarchy."
                    $help_div.append(data.name + " : " + description);
                }
            })
        } else {
            if ($help_div.length){
                $help_div.empty();
            }
        }
    }
})