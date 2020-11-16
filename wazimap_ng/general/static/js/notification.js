$(document).ready(function ($) {
    // Mark notifications as viewed
    $(".notification-body").on("click", ".delete-notification", function () {
        let $li = $(this).parents(".dropmic-menu__listItem");
        delete_notification($li);
    });

    $(".mark_as_read").on("click", function () {
        $.ajax({
            url: '/inbox/notifications/delete/all/',
            success: function () {
                $(".completed ul li").remove();
            }
        });
    });
});

function mark_notifications_as_viewed() {
    $.ajax({
        url: '/inbox/notifications/mark-all-as-read/',
        success: function () {
            $("#notification-box .has-badge").attr("data-count", 0);
            $("#notification-box button").removeClass("has-badge");
        }
    });
}

function remove_viewed_icons() {
    $("#notification-box .unread").remove();
}

function delete_notification($li) {
    $.ajax({
        url: '/inbox/notifications/delete/' + $li.data("slug") + "/",
        success: function () {
            $li.animate({"left": "-1000px"}, "slow").remove();
        }
    });
}

function custom_fetch_api_data() {
    $.ajax({
        url: '/inbox/notifications/active_notifications/',
        success: function (data) {
            console.log(data);
            if (data.count > 0) {
                $("#notification-box button").addClass("has-badge").attr("data-count", data.count);
            } else {
                $("#notification-box button").removeClass("has-badge").attr("data-count", 0);
            }
            let $in_progress_ul = $(".notification-body .in-progress ul");
            let $completed_ul = $(".notification-body .completed ul");
            $in_progress_ul.html("");
            $.each(data.in_progress, function (idx, notification) {
                $in_progress_ul.append(notification.html);
            });
            $completed_ul.html("");
            $.each(data.completed, function (idx, notification) {
                $completed_ul.append(notification.html);
            });
            $("#total-count").html(data.total_active_count);
            $("#in-progress-count").html(data.in_progress_count);
            $("#completed-count").html(data.completed_count);
        }
    });
}
