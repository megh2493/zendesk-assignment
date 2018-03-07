// code to implement pagination
$(document).ready(function() {
    cur_page = 1;
    num_pages = $('tbody').length;
    $('#first').click(function() {
        $('#tbody-'+cur_page).hide(0);
        cur_page = 1;
        $('#tbody-'+cur_page).show(0);
        $('#prev').addClass('disabled');
        $('#first').addClass('disabled');
        $('#next').removeClass('disabled');
        $('#last').removeClass('disabled');
    });
    $('#prev').click(function() {
        $('#tbody-'+cur_page).hide(0);
        --cur_page;
        $('#tbody-'+cur_page).show(0);
        if(cur_page == 1) {
            $('#prev').addClass('disabled');
            $('#first').addClass('disabled');
        }
        $('#next').removeClass('disabled');
        $('#last').removeClass('disabled');
    });
    $('#next').click(function() {
        $('#tbody-'+cur_page).hide(0);
        ++cur_page;
        $('#tbody-'+cur_page).show(0);
        if(cur_page == num_pages) {
            $('#next').addClass('disabled');
            $('#last').addClass('disabled');
        }
        $('#prev').removeClass('disabled');
        $('#first').removeClass('disabled');
    });

    $('#last').click(function() {
        $('#tbody-'+cur_page).hide(0);
        cur_page = num_pages;
        $('#tbody-'+cur_page).show(0);
        $('#next').addClass('disabled');
        $('#last').addClass('disabled');
        $('#prev').removeClass('disabled');
        $('#first').removeClass('disabled');
    });
});