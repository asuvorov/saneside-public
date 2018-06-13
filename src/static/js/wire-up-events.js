(function ($) {
    /***
      * This Javascript Code checks for the Browser/Browser Tab Action.
      * It is based on the File, mentioned by Daniel Melo.
      * Reference: http://stackoverflow.com/questions/1921941/close-kill-the-session-when-the-browser-or-tab-is-closed
     ***/
    var validNavigation = false;
    var leaveMessage = "" +
        "Ooops...\n\n" +
        "It feels like you are in the middle of something...\n" +
        "Please, check the Data for Errors and finish completing the Form...";

    function wireUpEvents() {
        /***
          * For a List of Events, that triggers `onbeforeunload` on IE,
          * check http://msdn.microsoft.com/en-us/library/ms536907(VS.85).aspx
         ***/
        console.log(">>> INSIDE : wireUpEvents()");

        window.onbeforeunload = function(event) {
            var event = window.event || event;

            event.preventDefault();

            console.log(">>> INSIDE : onbeforeunload");
            console.log(">>> ValidNavigation : " + validNavigation);

            if (!validNavigation) {
                // e.message is optional
                return "You have already inputed some text. Sure to leave?" || leaveMessage;
            }
        }

        // --- Attach the `keypress` Event to exclude the F5 Refresh
        $(document).bind("keypress", function(e) {
            if (e.keyCode == 116) {
                validNavigation = true;
            }
        });

        // --- Attach the `click` Event for all of the Links on the Page
        $("a").bind("click", function() {
            validNavigation = true;
        });

        // --- Attach the `submit` Event for all of the Forms on the Page
        $("form").bind("submit", function() {
            validNavigation = true;
        });

        // --- Attach the `click` Event for all of the Inputs on the Page
        $("input[type=submit]").bind("click", function() {
            validNavigation = true;
        });
    }

    // ------------------------------------------------------------------------
    // --- Wire up the Events as soon as the DOM Tree is ready
    $(document).ready(function() {
        console.log(">>> INSIDE : document.ready");

        wireUpEvents();
    });
})(jQuery);
