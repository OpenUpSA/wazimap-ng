(function($) {
    jQuery(document).ready(function($) {

        changeElDisplay("indicatordata_form", "none")
        createSelectOption();

        function selectOnChange(val) {
            if (val == "2") {
                changeElDisplay("indicatordata_form", "block");
                changeElDisplay("add_method__div", "none");
            } else {
                changeElDisplay("indicatordata_form", "none");
            }
        }


        function changeElDisplay(id, display) {
            var el = document.getElementById(id);
            el.style.display = display;
        }
        
        function createSelectOption() {
            var selDiv = document.createElement("div");
            selDiv.setAttribute("class", "form-row aligned");
            selDiv.setAttribute("id","add_method__div");
    
            var sel = document.createElement("select");
            sel.setAttribute("id","add_method");
            sel.onchange = function() { selectOnChange(this.value)};
    
            var selLabel = document.createElement("Label");
            selLabel.setAttribute("for", "add_method");
            selLabel.setAttribute("class", "required")
            selLabel.innerHTML = "Choose add method";
    
            var optionValues = {
                0:"----------------------", 
                1:"Upload an indicator director",
                2:"Create from dataset"
            }
            for (key in optionValues) {
                var opt = document.createElement("option");
                if (key == "0") {
                    opt.value = ""
                } else {
                    opt.value = key;
                }
                opt.text = optionValues[key];
                sel.add(opt)
            }
    
            var content = document.getElementById("content-main");
            selDiv.appendChild(selLabel);
            selDiv.appendChild(sel);
            content.appendChild(selDiv);

        }

    });
})(django.jQuery);
