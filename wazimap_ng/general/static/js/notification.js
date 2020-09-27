$(document).ready(function($) {

  // Mark notifications as viewed
  $(".notification-body").on("click", ".delete-notification", function(){
    let $li = $(this).parents(".dropmic-menu__listItem");
    delete_notification($li);
    change_count($("#complete-count"), -1);
  });

  $(".mark_as_read").on("click", function(){
    $.ajax({
        url:'/notifications/delete-notification/all/',
        success:function(data) {
          let len = $(".completed .dropmic-menu__listItem").length;
          console.log(-len);
          $(".completed ul li").remove();
          change_count($("#complete-count"), -len);
        }
     });
  });

  setInterval(fetch_api_data, 10000);
});

function mark_notifications_as_viewed(){
  let count = $("#notification-box .has-badge ").data("count");

  if (count > 0){
    $.ajax( {
        url:'/notifications/mark-all-as-read/',
        success:function(data) {
           $("#notification-box .has-badge").attr("data-count", 0);
           $("#notification-box button").removeClass("has-badge");
        }
     });
  }
}

function remove_viewed_icons(){
  $("#notification-box .unread").remove();
}

function delete_notification($li){
  $.ajax( {
      url:'/notifications/delete-notification/'+$li.data("id")+"/",
      success:function(data) {
         $li.animate({"left":"-1000px"}, "slow").remove();
      }
   });
}

function change_count($elm, diff){
  let
    $totalCount = $("#total-count"),
    elm_count = parseInt($elm.html()) + diff,
    total_count = parseInt($totalCount.html()) + diff;

  $elm.html(elm_count);
  $totalCount.html(total_count);

  check_if_0($elm, elm_count);
}

function check_if_0($elm, elm_count){
  let msg = "";
  if (elm_count == 0){
    if($elm.attr('id') == "complete-count"){
      msg = "No New Notification";
    } else if($elm.attr('id') == "in-progress-count") {
      msg = "No Task in progress right now";
    }
    $elm.parents(".completed").find("ul").append(
      "<li class='no_task'>"+msg+"</li>"
    );
  }
}

function fetch_api_data(){
  $.ajax( {
      url:'/notifications/unread-notifications/',
      success:function(data) {
         if(data.results.length > 0){

           $("#notification-box button").addClass("has-badge").attr(
              "data-count", data.results.length
            )
           let $in_progress_ul = $(".notification-body .in-progress ul");
           let $completed_ul = $(".notification-body .completed ul")
           $.each(data.results, function(idx, notification){
             if (notification.level == "in_progress"){
               let is_present = $in_progress_ul.find(
                 "[data-id="+ notification.id +"]"
               ).length > 0;
               if(!is_present){
                 if($in_progress_ul.find(".no_task").length > 0){
                   $in_progress_ul.find(".no_task").remove()
                 }
                 $in_progress_ul.prepend(notification.html);
                 change_count($("#in-progress-count"), 1)
               }
             } else {
               let progress_notification = $in_progress_ul.find(
                 "[data-id="+ notification.id +"]"
               );

               if(progress_notification.length > 0){
                 progress_notification.remove();
               }
               let is_present = $completed_ul.find(
                 "[data-id="+ notification.id +"]"
               ).length > 0;

               if(!is_present){
                 if($completed_ul.find(".no_task").length > 0){
                   $completed_ul.find(".no_task").remove()
                 }
                 $completed_ul.prepend(notification.html);
                 change_count($("#complete-count"), 1)
              }
             }
           });
         }
      }
   });
}
