var Team = Team || {};

Team.Users = {};

(function (window, $) {
  "use strict";

  var options,
    $main,
    $addBtn,
    $users,
    $groups,
    $usersList,
    $loader,
    $originalMsg,
    usrTmpl = [
      "<tr>",
      '<td class="usr"></td>',
      '<td class="grp"></td>',
      "<td>",
      '<button class="remove-usr btn btn-danger btn-sm" data-bs-toggle="modal" data-bs-target="#removeModal">',
      '<i class="fa fa-times"></i>',
      "</button>",
      "</td>",
      "</tr>",
    ].join("");

  function init(opts) {
    options = $.extend(
      {
        addUrl: "",
        deleteUrl: "",
        listUrl: "",
      },
      opts
    );

    $main = $("#add-user-team");
    $addBtn = $main.find(".add-btn");
    $users = $main.find(".users");
    $groups = $main.find(".groups");
    $usersList = $main.find(".related-users");
    $loader = $main.find(".loader-gif");
    $originalMsg = $(
      "#removeModal > .modal-dialog > .modal-content > .modal-body > p"
    ).text();

    if (!Team.Users.wasCalled) {
      bindEvents();
    }

    Team.Users.wasCalled = true;

    Base.CSRF.fix();
    fillUsersAndTeams();
  }

  function bindEvents() {
    $addBtn.on("click", function (e) {
      e.preventDefault();

      var $item = $(usrTmpl),
        $usr = $users.find("option:selected"),
        $grp = $groups.find("option:selected");

      $item.data({ userId: $usr.val(), groupId: $grp.val() });
      $item.find(".usr").text($usr.text());
      $item.find(".grp").text($grp.text());

      addUserTeam($item);
    });

    $main.on("click", ".remove-usr", function (e) {
      e.preventDefault();
      let $row = $(this).closest("tr");
      let $usr = $row.children(".usr").text();
      let $grp = $row.children(".grp").text();
      let $message = $(
        "#removeModal > .modal-dialog > .modal-content > .modal-body > p"
      );
      let $newMsg = $originalMsg.slice();
      $newMsg = $newMsg.replace("{usr}", $usr).replace("{grp}", $grp);

      $message.text($newMsg);
      let $confirmBtn = $("#removeModalConfirm");
      $confirmBtn.on("click", function (e) {
        removeUserTeam($row);
      });
    });
  }

  function fillUsersAndTeams() {
    $.ajax({
      type: "POST",
      url: options.listUrl,
    })
      .done(function (data) {
        buildUsers(data);
      })
      .fail(function (data) {
        Base.Messages.setMessage({
          description: data.responseJSON.msg,
          type: "error",
        });
      });
  }

  function buildUsers(data) {
    var $content = $("<div></div>"),
      users_teams = data,
      $temp;

    for (var i = 0, l = users_teams.length; i < l; i++) {
      var user = users_teams[i].team.users;
      var team = users_teams[i].team;

      $temp = $(usrTmpl);
      $temp.data({ userId: user.id, groupId: team.id });
      $temp.find(".usr").text(user.name);
      $temp.find(".grp").text(team.name);

      $usersList.find("tbody").append($temp);
    }
    showTeamsUsersList();
  }

  function showTeamsUsersList() {
    $loader.fadeOut("fast").remove();
    $usersList.fadeIn("fast");
  }

  function addUserTeam($item) {
    $.ajax({
      type: "POST",
      url: options.addUrl,
      data: {
        user: $item.data("userId"),
        group: $item.data("groupId"),
      },
    })
      .done(function (data) {
        $usersList.append($item);
      })
      .fail(function (data) {
        Base.Messages.setMessage({
          description: data.responseJSON.msg,
          type: "error",
        });
      });
  }

  function removeUserTeam($item) {
    $.ajax({
      type: "POST",
      url: options.deleteUrl,
      data: {
        user: $item.data("userId"),
        group: $item.data("groupId"),
      },
    })
      .done(function (data) {
        $item.remove();
        Base.Messages.setMessage({
          description: "User removed",
          type: "success",
        });
        refreshComponent($groups);
        reloadWindowsAjax();
      })
      .fail(function (data) {
        Base.Messages.setMessage({
          description: data.responseJSON.msg,
          type: "error",
        });
      });
  }

  function refreshComponent(seletor) {
    $(seletor).trigger("chosen:updated");
  }

  function reloadWindowsAjax() {
    location.reload();
  }

  $.extend(Team.Users, {
    wasCalled: false,
    init: init,
  });
})(window, jQuery);
