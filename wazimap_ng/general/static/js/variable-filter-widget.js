(function($) {
    jQuery(document).ready(function($) {
        $(function () {
            $("#variable-permission-filter input[name='variable_type']" ).on('change', ChangeVaribaleValues);
        });

        function ChangeVaribaleValues() {
            let permissionType = $(this).val();
            let hiddenPermissionType = permissionType == "public" ? "private": "public";
            $("#id_indicator").find("[data-type='"+permissionType+"']").removeClass("hidden");
            $("#id_indicator").find("[data-type='"+hiddenPermissionType+"']").addClass("hidden");
            $(document).find("#id_indicator option[value='']").attr('selected', true);
        }
    });
})(django.jQuery);
