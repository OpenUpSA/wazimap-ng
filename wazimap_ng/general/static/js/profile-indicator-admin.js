(function ($) {
    jQuery(document).ready(function ($) {
        const $profileEl = $(document).find("#id_profile");
        const $subcategoryEl = $(document).find("#id_subcategory");
        const $emptyOptionEl = $("<option></option>");

        $profileEl.on('change', function (e) {
            // trigger "loadSubcategory" func only when it was manually changed
            if (e.originalEvent !== undefined) {
                // load subcategories based on selected profile
                loadSubcategory(e.target.value);
            }
        });

        function appendOptionEl($outerEl, val, text){
            $outerEl.append($emptyOptionEl.clone().attr("value", val).text(text));
        }

        function clearSubcategories() {
            $subcategoryEl.empty();
            appendOptionEl($subcategoryEl, "", "-----------")
        }

        function loadSubcategory(selectedProfile) {
            if (selectedProfile) {
                var url = `/api/v1/profiles/${selectedProfile}/subcategories/`;
                $.ajax({
                    url: url,
                    success: function (data) {
                        // clear it here to avoid "select" input flickering which appears during AJAX call
                        clearSubcategories();
                        $.each(data, function (key, value) {
                            appendOptionEl($subcategoryEl, value.id, value.name)
                        });
                    }
                })
            } else {
                clearSubcategories();
            }
        }

        $(document).find("#id_indicator").on("change", function(){
            let contentType = $(this).find(":selected").data("contenttype");
            if (contentType == "qualitative"){
                $(".field-choropleth_method").hide();
                $(".field-chart_configuration").parents("fieldset").hide();
            } else {
                $(".field-choropleth_method").show();
                $(".field-chart_configuration").parents("fieldset").show();
            }
        });
    });
})(django.jQuery);

