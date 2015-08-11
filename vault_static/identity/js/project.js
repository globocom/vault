var Project = Project || {};


Project.Users = {};

(function(window, $) {
    'use strict';

    var options,
        $main, $addBtn, $users, $roles, $usersList, $loader,
        usrTmpl = ['<tr>',
                     '<td class="usr"></td>',
                     '<td class="rle"></td>',
                     '<td>',
                       '<a href="#" class="remove-usr btn btn-danger btn-xs">',
                         '<i class="fa fa-times"></i>',
                       '</a>',
                     '</td>',
                   '</tr>'].join('');

    function init(opts) {
        options = $.extend({
            'projectId': '',
            'addUrl': '',
            'deleteUrl': '',
            'listUrl': ''
        }, opts);

        $main = $('#add-user-role');
        $addBtn = $main.find('.add-btn');
        $users = $main.find('.users');
        $roles = $main.find('.roles');
        $usersList = $main.find('.related-users');
        $loader = $main.find('.loader');

        if (!Project.Users.wasCalled) {
            bindEvents();
        }

        Project.Users.wasCalled = true;

        fixCSRF();
        fillUsers();
    }

    function bindEvents() {
        $addBtn.on('click', function(e) {
            e.preventDefault();

            var $item = $(usrTmpl),
                $usr = $users.find('option:selected'),
                $rle = $roles.find('option:selected');

            $item.data({ 'userId': $usr.val(), 'roleId': $rle.val() });
            $item.find('.usr').text($usr.text());
            $item.find('.rle').text($rle.text());

            addUserRole($item);
        });

        $main.on('click', '.remove-usr', function(e) {
            e.preventDefault();
            removeUserRole($(this).closest('tr'));
        });
    }

    function fillUsers() {
        $.ajax({
            type: "POST",
            url: options.listUrl,
            data: {
                project: options.projectId
            }
        })
        .done(function (data) {
            buildUsers(data);
        })
        .fail(function (data) {
            Base.Messages.show(data.responseJSON.msg, 'error');
        });
    }

    function buildUsers(data) {
        var $content = $('<div></div>'),
            users = data.users,
            $temp;

        for(var i = 0, l = users.length; i < l; i++) {
            var roles = users[i].roles;

            for(var j = 0, k = roles.length; j < k; j++) {
                $temp = $(usrTmpl);
                $temp.data({ 'userId': users[i].id, 'roleId': roles[j].id });
                $temp.find('.usr').text(users[i].username);
                $temp.find('.rle').text(roles[j].name);

                $usersList.find('tbody')
                          .append($temp);
            }
        }
        showUsersList();
    }

    function showUsersList() {
        $loader.fadeOut('fast').remove();
        $usersList.fadeIn('fast');
    }

    function addUserRole($item) {
        $.ajax({
            type: "POST",
            url: options.addUrl,
            data: {
                project: options.projectId,
                user: $item.data('userId'),
                role: $item.data('roleId')
            }
        })
        .done(function (data) {
            $usersList.append($item);
        })
        .fail(function (data) {
            Base.Messages.show(data.responseJSON.msg, 'error');
        });
    }

    function removeUserRole($item) {
        $.ajax({
            type: "POST",
            url: options.deleteUrl,
            data: {
                project: options.projectId,
                user: $item.data('userId'),
                role: $item.data('roleId')
            }
        })
        .done(function (data) {
            $item.remove();
        })
        .fail(function (data) {
            Base.Messages.show(data.responseJSON.msg, 'error');
        });
    }

    function fixCSRF() {
        var csrftoken = Base.Util.getCookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.extend(Project.Users, {
        wasCalled: false,
        init: init
    });

})(window, jQuery);
