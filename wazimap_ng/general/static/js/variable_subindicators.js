(function($) {
    jQuery(document).ready(function($) {
        $(function () {
            $("#id_profile" ).on('change', loadSubCategories);
            $("#id_variable" ).on('change', loadSubindicators);
            $("#id_indicator" ).on('change', loadSubindicators);
        });

        function loadSubCategories() {
            var profileId = $(this).val();
            var $el = $("#id_subcategory");
            var profileName = $(this).find("option:selected").text()
            if (profileId) {
                var url = '/api/v1/profiles/' + profileId + '/categories/';
                var subcategories = [];
                $.ajax({
                    url: url,
                    success: function(data) {
                        $el.empty();
                        $el.append($("<option></option>").attr("value", "").text("----------"));
                        data.forEach(function(category) {
                            $.each(category.subcategories, function(key, sc) {
                                $el.append($("<option></option>").attr("value", sc.id).text(
                                    profileName+": "+ category.name + " -> " + sc.name
                                ));
                            });
                        });
                    }
                })
            } else{
                $el.empty();
                $el.append($("<option></option>").attr("value", "").text("----------"));
            }
        }

        function loadSubindicators() {
            var indicatorId = $(this).val();
            var $el = $("#id_subindicator");

            if(indicatorId) {
               var url = '/api/v1/indicators/' + indicatorId + "/";
                $.ajax({
                    url: url,
                    success: function (data) {
                        let subindicators = data.subindicators;
                        $el.empty();
                        $el.append($("<option></option>").attr("value", "").text("----------"));
                        $.each(subindicators, function(key, value) {
                            $el.append($("<option></option>").attr("value", key).text(value));
                        });

                    }
                });
            } else {
                $el.empty();
                $el.append($("<option></option>").attr("value", "").text("----------"));
            }
        }
    });
})(django.jQuery);
