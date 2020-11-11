(function ($) {
    jQuery(document).ready(function ($) {
        const $profileEl = $("#id_profile");
        const $subcategoryEl = $("#id_subcategory");

        $profileEl.on('change', function (e) {
            // load subcategories based on selected profile
            loadSubcategory(e.target.value);
        });

        function clearSubcategories() {
            $subcategoryEl.empty();
            $subcategoryEl.append($("<option></option>").attr("value", "").text("----------"));
        }

        function loadSubcategory(selectedProfile) {
            if (selectedProfile) {
                var url = `/api/v1/profiles/${selectedProfile}/subcategories/`;
                $.ajax({
                    url: url,
                    success: function (data) {
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

