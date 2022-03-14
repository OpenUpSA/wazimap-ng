(function ($) {
    jQuery(document).ready(function ($) {
        const $profileEl = $(document).find("#id_profile");
        const $versionEl = $(document).find("#id_version");
        const $emptyOptionEl = $("<option></option>");

        $profileEl.on('change', function (e) {
            // trigger "loadVersion" func only when it was manually changed
            if (e.originalEvent !== undefined) {
                // load loadVersion based on selected profile
                loadVersion(e.target.value);
            }
        });

        function appendOptionEl($outerEl, val, text){
            $outerEl.append($emptyOptionEl.clone().attr("value", val).text(text));
        }

        function clearVersions() {
            $versionEl.empty();
            appendOptionEl($versionEl, "", "-----------")
        }

        function loadVersion(selectedProfile) {
            if (selectedProfile) {
                var url = `/api/v1/profiles/${selectedProfile}/versions/`;
                $.ajax({
                    url: url,
                    success: function (data) {
                        clearVersions();
                        $.each(data, function (key, value) {
                            appendOptionEl($versionEl, value.id, value.name)
                        });
                    },
                    error: function (jqXHR, exception) {
                      clearVersions();
                      toastr["error"]("Something went wrong while fetching versions.")
                    }
                })
            } else {
                clearVersions();
            }
        }
    });
})(django.jQuery);
