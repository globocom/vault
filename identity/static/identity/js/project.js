var Project = Project || {};

Project.Users = {
  wasCalled: false,
};

(function (window, $) {
  "use strict";

  var options,
    $main,
    $addBtn,
    $users,
    $roles,
    $usersList,
    $loader,
    timeout = 120000,
    usrTmpl = [
      "<tr>",
      '<td class="usr"></td>',
      '<td class="rle"></td>',
      "<td>",
      '<a href="#" class="remove-usr btn btn-danger btn-sm">',
      '<i class="fa fa-times"></i>',
      "</a>",
      "</td>",
      "</tr>",
    ].join("");

  function init(opts) {
    options = $.extend(
      {
        projectId: "",
        addUrl: "",
        deleteUrl: "",
        listUrl: "",
        resetPassUrl: "",
        resetMsg: "Confirm reset password?",
      },
      opts
    );

    $main = $("#add-user-role");
    $addBtn = $main.find(".add-btn");
    $users = $main.find(".users");
    $roles = $main.find(".roles");
    $usersList = $main.find(".related-users");
    $loader = $main.find(".users-loading");

    if (!Project.Users.wasCalled) {
      bindEvents();
    }

    Project.Users.wasCalled = true;

    Base.CSRF.fix();
    fillUsers();
  }

  function bindEvents() {
    $addBtn.on("click", function (e) {
      e.preventDefault();

      var $item = $(usrTmpl),
        $usr = $users.find("option:selected"),
        $rle = $roles.find("option:selected");

      const usrId = $usr.val();
      const rleId = $rle.val();

      $item.data({ userId: usrId, roleId: rleId });
      $item.find(".usr").text($usr.text());
      $item.find(".rle").text($rle.text());

      if (usrId === "" || rleId === "") {
        Base.Messages.setMessage({
          type: "warning",
          description: "Select user and role",
        });

        return;
      }

      addUserRole($item);
    });

    $main.on("click", ".remove-usr", function (e) {
      e.preventDefault();
      removeUserRole($(this).closest("tr"));
    });

    var $form = $(".project-form");

    $form.on("click", ".reset-pass", function () {
      if (window.confirm(options.resetMsg)) {
        $(".reset-pass").attr("disabled", true);
        resetPassword();
      }
      return false;
    });
  }

  function resetPassword() {
    var $reset_info = $(".reset-info");
    var $resetLoading = $(".reset-loading");
    $resetLoading.show();
    $.ajax({
      type: "POST",
      url: options.resetPassUrl,
      data: {
        project: options.projectId,
      },
      timeout: timeout,
    })
      .done(function (data) {
        $resetLoading.hide();
        $reset_info
          .addClass("visible")
          .find(".new-pass")
          .text(data.new_password);
        Base.Messages.setMessage({
          description: "Password reset success",
          type: "success",
        });
      })
      .fail(function (data) {
        Base.Messages.setMessage({
          description: "Error on reset password",
          type: "error",
        });
      });
  }

  // function showPassword(data) {
  //   var new_user_password = data['new-password']
  //   var $divPassword = $('.user_password');

  //   $divPassword.fadeToggle( "slow", "linear", function() {
  //     $divPassword.html('NEW PASSWORD: ' + new_user_password);
  //   });
  // }

  function fillUsers() {
    $.ajax({
      type: "GET",
      url: `${options.listUrl}?project_id=${options.projectId}`,
      timeout: timeout,
    })
      .done(function (data) {
        buildUsers(data);
      })
      .fail(function (data) {
        Base.Messages.setMessage({
          description: data.statusText,
          type: "error",
        });
      });
  }

  function buildUsers(data) {
    const users = data.users;
    let $temp;

    for (var i = 0, l = users?.length; i < l; i++) {
      var roles = users[i].roles;

      for (var j = 0, k = roles.length; j < k; j++) {
        $temp = $(usrTmpl);
        $temp.data({ userId: users[i].id, roleId: roles[j].id });
        $temp.find(".usr").text(users[i].username);
        $temp.find(".rle").text(roles[j].name);

        $usersList.find("tbody").append($temp);
      }
    }
    showUsersList();
  }

  function showUsersList() {
    $loader.fadeOut("fast").remove();
    $usersList.fadeIn("fast");
  }

  function addUserRole($item) {
    $.ajax({
      type: "POST",
      url: options.addUrl,
      data: {
        project: options.projectId,
        user: $item.data("userId"),
        role: $item.data("roleId"),
      },
      timeout: timeout,
    })
      .done(function (data) {
        $usersList.append($item);
        Base.Messages.setMessage({
          description: "Role added.",
          type: "success",
        });
      })
      .fail(function (data) {
        Base.Messages.setMessage({
          description: data.statusText,
          type: "error",
        });
      });
  }

  function removeUserRole($item) {
    $.ajax({
      type: "POST",
      url: options.deleteUrl,
      data: {
        project: options.projectId,
        user: $item.data("userId"),
        role: $item.data("roleId"),
      },
      timeout: timeout,
    })
      .done(function (data) {
        $item.remove();
        Base.Messages.setMessage({
          description: "Role removed.",
          type: "success",
        });
      })
      .fail(function (data) {
        Base.Messages.setMessage({
          description: data.statusText,
          type: "error",
        });
      });
  }

  $.extend(Project.Users, {
    init: init,
  });
})(window, jQuery);
