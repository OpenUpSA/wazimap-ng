$(function () {
    $("#id_variable" ).on('change', loadSubindicators);
    $("#id_indicator" ).on('change', loadSubindicators);
});

function loadSubindicators(){
    var indicatorId = $(this).val();

    if(indicatorId){
       var url = `/api/v1/indicators/${indicatorId}/`;

        $.ajax({
            url: url,
            success: function (data) {

                let subindicators = data.subindicators;
                let newOptions = subindicators.reduce(
                    function(o, val) { o[val] = val; return o; }, {}
                );

                var $el = $("#id_subindicator");
                $el.empty();
                $el.append($("<option></option>").attr("value", "").text("----------"));
                $.each(newOptions, function(key, value) {
                    $el.append($("<option></option>").attr("value", value).text(key));
                });
                
            }
        });
    }
}
