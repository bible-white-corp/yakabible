// Navbar stylée
(function ($) {
    $(document).ready(function () {
        var offset = $("#nav").offset().top;
        $("#navproxy").height($("#nav").outerHeight(true));
        $(document).scroll(function () {
            var scrollTop = $(document).scrollTop();
            if (scrollTop > offset) {
                $("#nav").addClass("fixed-top");
                $("#navproxy").css("display", "block");
            }
            else {
                $("#nav").removeClass("fixed-top");
                $("#navproxy").css("display", "none");
            }
        });
        $(document).resize(function () {
            offset = $("#nav").offset().top;
            $("#navproxy").height($("#nav").outerHeight(true));
        });
    });
})(jQuery);