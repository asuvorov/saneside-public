(function ($) {
    // ------------------------------------------------------------------------
    // --- Initialize NavBar Wizard
    $(document).ready(function () {
        // $(".nav-tabs > li a[title]").tooltip();
        $("a[data-toggle='tab']").on("show.bs.tab", function (e) {
            var $target = $(e.target);

            if ($target.parent().hasClass("disabled")) {
                return false;
            }

            smoothScroll($(".tab-pane.active"));
        });
        $(".next-step").click(function (e) {
            var $active = $(".wizard .nav-tabs li.active");

            var element = $(this);

            var hasErrors = false;

            // ----------------------------------------------------------------
            // --- Validate Form Fields on the active Tab before proceeding.
            //     This is supposed to cover all the possible Forms on the
            //     Platform:
            //     1) Checking the Values of the required Field(s);
            //     2) Checking the Values of the Email Field(s), if they
            //        correspond with the RegExp;
            //     3) Checking the Values of the URL Field(s), if they
            //        correspond with the RegExp;
            //     4) Checking the Value of `id_addressless` CheckBox, and if
            //        it's not checked, then some of the Address Fields should
            //        be treated, as required;
            //     5) Checking the Value of `id_contact_1` (Alt Person)
            //        RadioBox, and if it's checked, then some of the
            //        Alt Person Fields should be treated, as required;
            //     6) Checking Value of `id_recurrence`, and if it's not
            //        "dateless", then some of the start Date/Time Fields
            //        should be treated, as required.
            //     7) Checking the Value of `id_accept_automatically` CheckBox,
            //        and if it's checked, then `id_acceptance_text` Field
            //        should be treated, as required;

            // ----------------------------------------------------------------
            // --- Collect and loop DIV Tags, wrapping up the INPUT Tags.
            var divs = $(element).parent().parent().parent().find("div.form-group");

            $.each(divs, function (i, div) {
                // ------------------------------------------------------------
                // --- Collect and loop INPUT Tags.
                var inputs = $(div).find("input[id*='id_'], textarea[id*='id_']");

                if (inputs.length > 0) {
                    $.each(inputs, function (j, input) {
                        console.log(">>> INPUT  : ", input);
                        console.log(">>>  TYPE  : ", $(input).prop("type"));

                        // ----------------------------------------------------
                        // --- (7) Check `id_accept_automatically` CheckBox.
                        if ($("#id_accept_automatically").prop("checked")) {
                            var is_valid = $(input).val();

                            if ($(input).prop("id") == "id_acceptance_text") {
                                if (!is_valid) {
                                    $(div).addClass("has-error");
                                    $(div).find("span.help-block").html("This Field is required.");

                                    hasErrors = true;

                                    return false;
                                } else {
                                    $(div).removeClass("has-error");
                                    $(div).find("span.help-block").html("");
                                }
                            }
                        }

                        // ----------------------------------------------------
                        // --- (4) Check `id_addressless` CheckBox.
                        if ($("#id_addressless").prop("checked")) {
                            if ($(input).prop("id") == "id_address_1" ||
                                $(input).prop("id") == "id_city" ||
                                $(input).prop("id") == "id_zip_code") {

                                $(div).removeClass("has-error");
                                $(div).find("span.help-block").html("");

                                return true;
                            }
                        }

                        // ----------------------------------------------------
                        // --- (5) Check `id_contact_1` (Alt Person) RadioBox.
                        var selected = $("input[type='radio']:checked");

                        if (selected.val() == "he") {
                            var is_valid = $(input).val();

                            if ($(input).prop("id") == "id_alt_person_fullname" ||
                                $(input).prop("id") == "id_alt_person_email" ||
                                $(input).prop("id") == "id_alt_person_phone") {

                                if (!is_valid) {
                                    $(div).addClass("has-error");
                                    $(div).find("span.help-block").html("This Field is required.");

                                    hasErrors = true;

                                    return false;
                                } else {
                                    $(div).removeClass("has-error");
                                    $(div).find("span.help-block").html("");
                                }
                            }
                        }

                        // ----------------------------------------------------
                        // --- (6) Check `id_recurrence` CheckBox.
                        var option = $("#id_recurrence option:selected").text();

                        if (option == "Once") {
                            var is_valid = $(input).val();

                            if ($(input).prop("id") == "id_start_date" ||
                                $(input).prop("id") == "id_start_time" ||
                                $(input).prop("id") == "id_tz") {

                                if (!is_valid) {
                                    $(div).addClass("has-error");
                                    $(div).find("span.help-block").html("This Field is required.");

                                    hasErrors = true;

                                    return false;
                                } else {
                                    $(div).removeClass("has-error");
                                    $(div).find("span.help-block").html("");
                                }
                            }
                        }

                        // ----------------------------------------------------
                        // --- (1) Check required Fields.
                        if ($(input).prop("required")) {
                            var is_valid = $(input).val();

                            if (!is_valid) {
                                $(div).addClass("has-error");
                                $(div).find("span.help-block").html("This Field is required.");

                                hasErrors = true;

                                return false;
                            } else {
                                $(div).removeClass("has-error");
                                $(div).find("span.help-block").html("");
                            }
                        }

                        // ----------------------------------------------------
                        // --- (2) Check Email Fields.
                        if ($(input).prop("type") == "email") {
                            var value = $(input).val();
                            var re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
                            var is_valid = true;

                            if (value) {
                                is_valid = re.test(value);
                            }

                            if (!is_valid) {
                                $(div).addClass("has-error");
                                $(div).find("span.help-block").html("Enter valid Email Address.");

                                hasErrors = true;

                                return false;
                            } else {
                                $(div).removeClass("has-error");
                                $(div).find("span.help-block").html("");
                            }
                        }

                        // ----------------------------------------------------
                        // --- (3) Check URL Fields.
                        if ($(input).prop("type") == "url") {
                            var value = $(input).val();
                            var re = /(http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?/;
                            var is_valid = true;

                            if (value) {
                                if (value.substring(0, 4) == "www.") {
                                    value = "http://www." + value.substring(4);
                                }

                                is_valid = re.test(value);
                            }

                            if (!is_valid) {
                                $(div).addClass("has-error");
                                $(div).find("span.help-block").html("Enter valid URL Address.");

                                hasErrors = true;

                                return false;
                            } else {
                                $(div).removeClass("has-error");
                                $(div).find("span.help-block").html("");
                            }
                        }
                    })
                }
            })

            if (hasErrors) {
                console.log(">>> Has Errors...");

                smoothScroll($(".has-error"));

                return false;
            }

            $active.next().removeClass("disabled");
            nextTab($active);
        });
        $(".prev-step").click(function (e) {
            var $active = $(".wizard .nav-tabs li.active");

            prevTab($active);
        });

        // --- Call Fix Footer
        //fixFooter();
    })

    // ------------------------------------------------------------------------
    // --- Tabs Wizard
    function nextTab (elem) {
        $(elem).next().find('a[data-toggle="tab"]').click();
    }
    function prevTab (elem) {
        $(elem).prev().find('a[data-toggle="tab"]').click();
    }

    // ------------------------------------------------------------------------
    // --- Smooth Scroll
    function smoothScroll (element) {
        $("html, body").animate({
            scrollTop:      $(element).first().offset().top - $(".wizard-inner").height() - $("nav").height() - 10
        }, 500);
    }
})(jQuery);
