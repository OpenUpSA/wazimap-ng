(function ($) {
    jQuery(document).ready(function ($) {
        const $profileEl = $(document).find("#id_profile");
        const $subcategoryEl = $(document).find("#id_subcategory");
        const $emptyOptionEl = $("<option></option>");
        const $permissionOptionEl = $(document).find("#variable-permission-filter");

        filterVariables($profileEl.val(), $permissionOptionEl.find("input:checked").val());

        $profileEl.on('change', function (e) {
            // trigger "loadSubcategory" func only when it was manually changed
            if (e.originalEvent !== undefined) {
                // load subcategories based on selected profile
                loadSubcategory(e.target.value);
                filterVariables(e.target.value, $permissionOptionEl.find("input:checked").val());
            }
        });

        $permissionOptionEl.on('change', function (e) {
            if (e.originalEvent !== undefined) {
                filterVariables($profileEl.val(), e.target.value);
            }
        });

        function appendOptionEl($outerEl, val, text) {
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

        function filterVariables(selectedProfile, permissionType) {
            $('select#id_indicator option').each(function () {
                if (this.value !== '') {
                    //filter out the first option
                    console.log({'this.value': this})
                }
            })
        }
    });
})(django.jQuery);

