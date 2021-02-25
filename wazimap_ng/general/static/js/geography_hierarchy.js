(function($){
    jQuery(document).ready(function($) {
        $(function () {
           loadHeirarchyHelpText()
            $("#id_geography_hierarchy").on('change', function() {
                loadHeirarchyHelpText();
            });

            $("#id_profile").on('change', function() {
                loadHeirarchyAccordingProfile();
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

        function loadHeirarchyAccordingProfile() {
            var profileID = $(document).find("#id_profile").val();
            var geographyHierarchyID = $(document).find("#id_geography_hierarchy").val();
            var $help_div = $(document).find(".field-geography_hierarchy .help");

            if (profileID) {
                var url = '/api/v1/profiles/' + profileID + "/";
                $.ajax({
                    url: url,
                    success: function(data) {

                        var hierarchyID = data.geography_hierarchy.id;

                        if (hierarchyID != geographyHierarchyID){
                            $(document).find("#id_geography_hierarchy").val(hierarchyID);
                            if ($help_div.length){
                                $help_div.empty();
                            }else{
                                $(document).find(".field-geography_hierarchy").append("<div class='help'></div>");
                                $help_div = $(document).find(".field-geography_hierarchy .help");
                            }
                            let description = data.geography_hierarchy.description.length ? data.geography_hierarchy.description : "Description not Provided for this hierarchy."
                            $help_div.append(data.name + " : " + description);
                        }

                    }
                })
            } else {
                if ($help_div.length){
                    $help_div.empty();
                }

                if (geographyHierarchyID){
                    $(document).find("#id_geography_hierarchy").val('');
                }
            }
        }
    });
})(django.jQuery);
