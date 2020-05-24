django.jQuery(document).ready(function($) {
    $(function () {
        $("#id_dataset").on('change', function() {
            loadGroups();
            loadUniverse();
        });
        $("#id_groups" ).on('change', loadUniverse);
        $("input[name='_addanother']").attr('type','hidden');
    });

    function loadGroups() {
        var datasetId = $(document).find("#id_dataset").val();
        if (datasetId) {
            var url = '/api/v1/datasets/' + datasetId + "/";
            var groups = [];
            $.ajax({
                url: url,
                success: function(data) {
                    groups = data.groups
                    var $el = $("#id_groups");
                    $el.empty();
                    $el.append($("<option></option>").attr("value", "").text("----------"));
                    $.each(groups, function(key, value) {
                        $el.append($("<option></option>").attr("value", value).text(value));
                    });
                }
            })
        }
    }
    
    function loadUniverse() {
        var datasetId = $(document).find("#id_dataset").val();
        var group = $(document).find("#id_groups").val();

        var url = '/api/v1/universe/';

        if (datasetId){
            let params = {"dataset": datasetId};
            if (group){
                params["group"] = group;
            }

            $.ajax({
                url: url,
                data: params,
                success: function (data) {
                    var $el = $("#id_universe");
                    var universes = data.results;
                    $el.empty();
                    $el.append($("<option></option>").attr("value", "").text("----------"));
                    $.each(universes, function(key, universe) {
                        $el.append($("<option></option>").attr("value", universe.id).text(universe.label));
                    });
                    
                }
            });
        }
           
    }
})