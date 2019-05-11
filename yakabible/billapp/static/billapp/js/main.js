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
            } else {
                $("#nav").removeClass("fixed-top");
                $("#navproxy").css("display", "none");
            }
        });
        $(document).resize(function () {
            offset = $("#nav").offset().top;
            $("#navproxy").height($("#nav").outerHeight(true));
        });
    });

    $(function () {
        var hash = window.location.hash;
        hash && $('ul.nav a[href="' + hash + '"]').tab('show');

        $('.nav-tabs a').click(function (e) {
            $(this).tab('show');
            var scrollmem = $('body').scrollTop();
            window.location.hash = this.hash;
        });
    });

})(jQuery);
