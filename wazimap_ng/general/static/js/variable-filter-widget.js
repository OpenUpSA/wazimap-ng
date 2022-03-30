(function ($) {
    jQuery(document).ready(function ($) {
        $(function () {
            $("#variable-permission-filter input[type='radio']").on('change', ChangeVariableValues);
            const $permissionOptionEl = $(document).find("#variable-permission-filter");
            const permissionTypes = {public: 'public', private: 'private'};
            const $profileEl = $(document).find("#id_profile");

            filterVariables(getProfileId($profileEl), $permissionOptionEl.find("input:checked").val(), false);

            $profileEl.on('change', function (e) {
                // trigger "loadSubcategory" func only when it was manually changed
                if (e.originalEvent !== undefined) {
                    // load subcategories based on selected profile
                    filterVariables(getProfileId($profileEl), $permissionOptionEl.find("input:checked").val(), true);
                }
            });

            $permissionOptionEl.on('change', function (e) {
                if (e.originalEvent !== undefined) {
                    filterVariables(getProfileId($profileEl), e.target.value, true);
                }
            });

            function ChangeVariableValues() {
                let permissionType = $(this).val();
                let hiddenPermissionType = permissionType == "public" ? "private" : "public";
                let parent = $(this).parents("div");
                parent.find("#id_indicator").find(`[data-type=${permissionType}]`).removeClass("hidden");
                parent.find("#id_indicator").find(`[data-type=${hiddenPermissionType}]`).addClass("hidden");
                parent.find("#id_indicator option[value='']").attr('selected', true);
            }

            function getProfileId($profileEl) {
                let profileId;
                if ($profileEl.length > 0) {
                    profileId = $profileEl.val();
                } else {
                    profileId = $('input[name=selected_profile_id]').val();
                }

                return profileId;
            }

            function filterVariables(selectedProfile, selectedPermissionType, changeSelectedOption) {
                console.log({selectedProfile, selectedPermissionType})
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
                        if (changeSelectedOption) {
                            //do not change the selected option on page load
                            $(this).prop('selected', true);
                        }
                    }
                })
            }
        });
    });
})(django.jQuery);