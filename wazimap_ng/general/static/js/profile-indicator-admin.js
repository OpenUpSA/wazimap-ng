(function ($) {
    jQuery(document).ready(function ($) {
        const $profileEl = $(document).find("#id_profile");
        const $subcategoryEl = $(document).find("#id_subcategory");

        $(document).find("#id_profile").on('change', function (e) {
            // trigger "loadSubcategory" func only when it was manually changed
            if (e.originalEvent !== undefined) {
                // load subcategories based on selected profile
                loadSubcategory(e.target.value);
            }
        });

        function clearSubcategories() {
            $subcategoryEl.empty();
            $subcategoryEl.append($("<option></option>").attr("value", "").text("----------"));
        }

        function loadSubcategory(selectedProfile) {
            console.log("selectedProfile", selectedProfile)
            if (selectedProfile) {
                var url = `/api/v1/profiles/${selectedProfile}/subcategories/`;
                $.ajax({
                    url: url,
                    success: function (data) {
                        // clear it here to avoid "select" input flickering which appears during AJAX call
                        clearSubcategories();
                        $.each(data, function (key, value) {
                            $subcategoryEl.append($("<option></option>").attr("value", value.id).text(value.name));
                        });
                    }
                })
            } else {
                clearSubcategories();
            }
        }
    });
})(django.jQuery);

