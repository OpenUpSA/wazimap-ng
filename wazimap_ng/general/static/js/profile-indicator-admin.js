(function ($) {
    jQuery(document).ready(function ($) {
        const $profileEl = $(document).find("#id_profile");
        const $subcategoryEl = $(document).find("#id_subcategory");
        const $emptyOptionEl = $("<option></option>");
        const $permissionOptionEl = $(document).find("#variable-permission-filter");
        const permissionTypes = {public: 'public', private: 'private'};

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

        function filterVariables(selectedProfile, selectedPermissionType) {
            if (selectedProfile === '' && selectedPermissionType === permissionTypes.private) {
                $('select#id_indicator').prop('disabled', true);
            } else {
                $('select#id_indicator').prop('disabled', false);
            }

            $('select#id_indicator option').each(function () {
                if (this.value !== '') {
                    //filter out the first option
                    let optionPermissionType = $(this).attr('data-type');
                    let optionProfile = $(this).attr('data-profileid');

                    let isHidden = false;
                    if (selectedPermissionType === permissionTypes.public && optionPermissionType !== permissionTypes.public) {
                        isHidden = true;
                    } else if (selectedPermissionType === permissionTypes.private && (optionProfile !== selectedProfile || optionPermissionType !== permissionTypes.private)) {
                        isHidden = true;
                    }

                    if (isHidden) {
                        $(this).addClass('hidden');
                    } else {
                        $(this).removeClass('hidden');
                    }
                } else {
                    $(this).prop('selected', true);
                }
            })
        }
    });
})(django.jQuery);

