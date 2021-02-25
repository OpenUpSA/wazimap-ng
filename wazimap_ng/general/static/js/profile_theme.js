(function($) {
    jQuery(document).ready(function($) {
        $(function () {
            $("#id_profile" ).on('change', loadThemes);
        });

        function loadThemes() {
            var profileId = $(this).val();
            var $el = $("#id_theme");
            if (profileId) {
                var url = '/api/v1/profile/' + profileId + '/points/themes/';
                var themes = [];
                $.ajax({
                    url: url,
                    success: function(data) {
                        data.forEach(function(theme) {
                            themes = themes.concat(theme);
                        })

                        var $el = $("#id_theme");
                        $el.empty()
                        var themeLabels = themes.map(function(theme) {
                            $el.append($("<option></option>").attr("value", theme.id).text(theme.name))
                        })
                    }
                })
            }
        }
    });
})(django.jQuery);
