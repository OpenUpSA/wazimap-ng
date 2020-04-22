django.jQuery(document).ready(function($) {
    $(function () {
        var $orignal_permissions = $("#permission_widget_container").clone();
        $("#id_profile_type>li>label" ).on('click', {orignal: $orignal_permissions}, hideShowContent);
        
        $( "form" ).submit(function( event ) {
            // event.preventDefault();
            let added = getAddedPerms();
            let removed = getRemovedPerms();

            $(this).append("<input type='hidden' name='permissions_added' value='"+added+"'>");
            $(this).append("<input type='hidden' name='permissions_removed' value='"+removed+"'>");
            

            // $(this).submit();
        });

    });

    function hideShowContent(event) {
        var permissionType = $(this).find("input").val();
        var $inner_element = event.data.orignal.clone();
        $("#permission_type_hidden").val(permissionType);

        if(permissionType == "non_editable"){
            $inner_element.find("input[class='view']").attr("checked", "checked");
            $inner_element.find("input[class='view']").attr("disabled", "disabled");
        }
        $(document).find(".permission_widget").html($inner_element.html());
        if(permissionType != "public"){
            $("#public-permission").addClass("hidden");
            $(".permission_widget").removeClass("hidden");
        } else {
            $("#public-permission").removeClass("hidden");
            $(".permission_widget").addClass("hidden");
        }
    }

    function getAddedPerms(){
        var added = {};
        $("#permission_widget_container input[type='checkbox']:checked").not("input[data-initial='true']").each(function(id, checkbox){
            let group_id = $(checkbox).parents(".row").find("input[name='group_id']").val();
            if(group_id in added){
                added[group_id].push(checkbox.name);
            }else{
                added[group_id] = [checkbox.name];
            }
        });
        return JSON.stringify(added);
    }

    function getRemovedPerms(){
        var removed = {};
        $("#permission_widget_container input[data-initial='true']").not("input[type='checkbox']:checked").each(function(id, checkbox){
            let group_id = $(checkbox).parents(".row").find("input[name='group_id']").val();
            if(group_id in removed){
                removed[group_id].push(checkbox.name);
            }else{
                removed[group_id] = [checkbox.name];
            }
        });
        return JSON.stringify(removed);
    }
})

