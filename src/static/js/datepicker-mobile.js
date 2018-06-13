(function($, Modernizr, window) {
    console.log("[---  INFO   ---] INSIDE DATEPICKER MOBILE JS");

    $(document).ready(function () {
        function bootstrapDatepickerMobile(ev) {
            var $inputs = $("input[name='birth_day'], input[name='start_date']");
            var isMobile = $(window).width() <= 480 || Modernizr.touch;

            console.log(">>> ELEMENTS :", $inputs);

            $inputs.each(function() {
                var $input = $(this);
                var val = $input.val();
                var valMoment;
                var isMoment = false;

                valMoment = moment(val);

                console.log(">>> DATE VAL        :", val);
                console.log(">>> DATE VAL MOMENT :", valMoment);

                if (val) {
                    isMoment = moment.isMoment(valMoment);
                }

                console.log(">>> IS MOBILE       :", isMobile);
                console.log(">>> IS MOMENT       :", isMoment);

                if (isMobile && Modernizr.inputtypes.date) {
                    if (isMoment) {
                        val = valMoment.format("YYYY-MM-DD");
                    }

                    $input.datepicker("destroy");
                    $input.val(val);
                    $input.attr("type", "date");
                } else {
                    if (isMoment) {
                        val = valMoment.format("MM/DD/YYYY");
                    }

                    $input.attr("type", "text");
                    $input.val(val);

                    if (isMobile) {
                        $input.datepicker("destroy");
                    } else {
                        $input.datepicker({
                            dateFormat:     "mm/dd/yy",
                            changeYear:     true,
                            changeMonth:    true
                        });

                        if (isMoment) {
                            $input.datepicker("setDate", valMoment.toDate());
                        }

                        if ($input.is(":focus")) {
                            $input.datepicker("show");
                        }
                    }
                }
            });
        }

        $(window).on("resize.bootstrapDatepickerMobile", bootstrapDatepickerMobile);

        bootstrapDatepickerMobile();
    })
}(jQuery, Modernizr, window));
