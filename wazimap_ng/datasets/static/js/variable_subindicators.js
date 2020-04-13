django.jQuery(document).ready(function($) {
    $(function () {
        $("#id_variable" ).on('change', loadSubindicators);
        $("#id_indicator" ).on('change', loadSubindicators);
    });
    
    function loadSubindicators(){
        var indicatorId = $(this).val();

        if(indicatorId){
           var url = '/api/v1/indicators/' + indicatorId + "/";

            $.ajax({
                url: url,
                success: function (data) {

                    let subindicators = data.subindicators;

                    var $el = $("#id_subindicator");
                    $el.empty();
                    $el.append($("<option></option>").attr("value", "").text("----------"));
                    $.each(subindicators, function(key, value) {
                        $el.append($("<option></option>").attr("value", value.id).text(value.label));
                    });
                    
                }
            });
        }
    }
})

