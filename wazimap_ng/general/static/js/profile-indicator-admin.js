(function ($) {
    jQuery(document).ready(function ($) {
        const $profileEl = $(document).find("#id_profile");
        const $subcategoryEl = $(document).find("#id_subcategory");
        const $emptyOptionEl = $("<option></option>");
        const $chartTypeEl = $(document).find("#id_chart_type");
        const $linearScrubber = $(document).find("#id_enable_linear_scrubber");

        showChartTypeDescription($chartTypeEl, $subcategoryEl);

        $linearScrubber.on('change', function (e) {
            loadHelpText(e.target.checked);
        });

        $profileEl.on('change', function (e) {
            // trigger "loadSubcategory" func only when it was manually changed
            if (e.originalEvent !== undefined) {
                // load subcategories based on selected profile
                loadSubcategory(e.target.value);
            }
        });

        $chartTypeEl.on('change', function () {
            showChartTypeDescription($chartTypeEl);
        })

        function appendOptionEl($outerEl, val, text) {
            $outerEl.append($emptyOptionEl.clone().attr("value", val).text(text));
        }

        function clearSubcategories() {
            $subcategoryEl.empty();
            appendOptionEl($subcategoryEl, "", "-----------")
        }

        function loadSubcategory(selectedProfile) {
            if (selectedProfile) {
                var url = `/api/v1/profiles/${selectedProfile}/subcategories/`;
                $.ajax({
                    url: url,
                    success: function (data) {
                        // clear it here to avoid "select" input flickering which appears during AJAX call
                        clearSubcategories();
                        $.each(data, function (key, value) {
                            appendOptionEl($subcategoryEl, value.id, value.name)
                        });
                    }
                })
            } else {
                clearSubcategories();
            }
        }

        function showChartTypeDescription($chartTypeEl) {
            const selectedVal = $chartTypeEl.val();
            const selectedSubcategory = $subcategoryEl.val();
            $(document).find('.field-chart_type .help').remove();
            if (selectedVal === "line") {
                let helpText = document.createElement("div");
                $(helpText).addClass('help');
                let html = `<span>Categories will be evenly spaced on a linear axis.
Ensure categories represent regular intervals and no categories are missing when using line charts.
Also <a href='../../../indicatorsubcategory/${selectedSubcategory}/change' target='_blank'>ensure your categories are ordered correctly</a></span>`;

                $(helpText).html(html);
                $(document).find('.field-chart_type').append(helpText);
            }
        }

        function loadHelpText(is_checked) {
          let helpTextLi = $linearScrubber.parent().find("li.alert-warning");
          if (is_checked){
            helpTextLi.show();
          } else {
            helpTextLi.hide();
          }
        }
    });
})(django.jQuery);
