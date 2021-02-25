(function($) {
    jQuery(document).ready(function($) {
        //check if add_method exist
        var el = document.getElementById("add_method_div");
        if (el) {
            var sel = document.getElementById("add_method");
            sel.onchange = function() { selectOnChange(this.value)};
            
            //hide indicator form
            showNode("indicatordata_form", "none");
        }

        function selectOnChange(val) {
            if (val == "1") {
                showNode("indicatordata_form", "none");
                var link = '/admin/datasets/indicatordata/upload';
                window.location.href = link;
            } else if (val == "2") {
                showNode("indicatordata_form", "block");
                //showNode("add_method_div", "none");
            } 
        }


        function showNode(id, display) {
            var el = document.getElementById(id);
            el.style.display = display;
        }

    });
})(django.jQuery);
