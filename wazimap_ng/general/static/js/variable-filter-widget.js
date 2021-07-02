(function($) {
    jQuery(document).ready(function($) {
        $(function () {
            $("#variable-permission-filter input[name='variable_type']" ).on('change', ChangeVaribaleValues);
        });

        function ChangeVaribaleValues() {
            console.log("IN");
            let permissionType = $(this).val();
            let hiddenPermissionType = permissionType == "public" ? "private": "public";
            let parent = $(this).parent()
            parent.find("#id_indicator").find("[data-type='"+permissionType+"']").removeClass("hidden");
            parent.find("#id_indicator").find("[data-type='"+hiddenPermissionType+"']").addClass("hidden");
            parent.find("#id_indicator option[value='']").attr('selected', true);
        }
    });
})(django.jQuery);