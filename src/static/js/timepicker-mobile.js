(function($, Modernizr, window) {
    console.log("[---  INFO   ---] INSIDE TIMEPICKER MOBILE JS");

    $(document).ready(function () {
        function bootstrapTimepickerMobile(ev) {
            var $inputs = $("input[name='start_time']");
            var isMobile = $(window).width() <= 480 || Modernizr.touch;

            console.log(">>> ELEMENTS :", $inputs);

            $inputs.each(function() {
                var $input = $(this);
                var val = $input.val();

                console.log(">>> TIME VAL :", val);

                if (isMobile && Modernizr.inputtypes.time) {
                    $input.timepicker("remove");
                    $input.val(val);
                    $input.attr("type", "time");
                } else {
                    $input.attr("type", "text");
                    $input.val(val);

                    if (isMobile) {
                        $input.timepicker("remove");
                    } else {
                        $input.timepicker({
                            timeFormat:             "h:i A",
                            step:                   30,
                            forceRoundTime:         true,
                            closeOnWindowScroll:    true,
                        });

                        $input.timepicker("setTime", val);

                        if ($input.is(":focus")) {
                            $input.timepicker("show");
                        }
                    }
                }
            });
        }

        $(window).on("resize.bootstrapTimepickerMobile", bootstrapTimepickerMobile);

        bootstrapTimepickerMobile();
    })
}(jQuery, Modernizr, window));
