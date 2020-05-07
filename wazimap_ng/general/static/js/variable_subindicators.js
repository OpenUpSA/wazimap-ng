django.jQuery(document).ready(function($) {
    $(function () {
        $("#id_profile" ).on('change', loadSubCategories);
        $("#id_variable" ).on('change', loadSubindicators);
        $("#id_indicator" ).on('change', loadSubindicators);

        loadSubCategories.call($("#id_profile"));
    });

    function loadSubCategories() {
        var profileId = $(this).val();
        if (profileId) {
            var url = '/api/v1/profiles/' + profileId + '/categories/';
            var subcategories = [];
            $.ajax({
                url: url,
                success: function(data) {
                    data.forEach(function(category) {
                        subcategories = subcategories.concat(category.subcategories);
                    })

                    var $el = $("#id_subcategory");
                    $el.empty()
                    var subcategoryLabels = subcategories.map(function(sc) {
                        $el.append($("<option></option>").attr("value", sc.id).text(sc.name))
                    })
                }
            })
        }
    }
    
    function loadSubindicators() {
        var indicatorId = $(this).val();

        if(indicatorId) {
           var url = '/api/v1/indicators/' + indicatorId + "/";

            $.ajax({
                url: url,
                success: function (data) {

                    let subindicators = data.subindicators;

                    var $el = $("#id_subindicator");
                    $el.empty();
                    $el.append($("<option></option>").attr("value", "").text("----------"));
                    $.each(subindicators, function(key, value) {
                        $el.append($("<option></option>").attr("value", key).text(value));
                    });
                    
                }
            });
        }
    }
})

