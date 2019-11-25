var Team = Team || {};


Team.UsersOGs = {};

(function(window, $) {
    'use strict';

    var $main, $groups, $ogs, $users, $usersList;

    function init() {
        $main = $('#search-user-team');
        $groups = $main.find('.groups');
        $ogs = $main.find('.ogs');
        $users = $main.find('.users');
        $usersList = $main.find('.related-users');

        bindEvents();
    }

    function bindEvents() {
        $groups.on('change', function(e) {
            e.preventDefault();
            $ogs.val('');
            $users.val('');
            $usersList.find('tbody tr').show()
            var searchGroup = this.options[e.target.selectedIndex].text;

            if (searchGroup === 'Todos') {
                return;
            }

            $usersList.find('tbody tr').each(function() {
                var group = $(this).find('td:first').text();
                if (searchGroup !== group) {
                    $(this).hide()
                }
            });
        });

        $ogs.on('change', function(e) {
            e.preventDefault();
            $groups.val('');
            $users.val('');
            $usersList.find('tbody tr').show()
            var searchOG = this.options[e.target.selectedIndex].text;

            if (searchOG === 'Todos') {
                return;
            }

            $usersList.find('tbody tr').each(function() {
                var og = $(this).find('td:eq(1)').text();
                if (searchOG !== og) {
                    $(this).hide()
                }
            });
        });

        $users.on('keyup', function(e) {
            e.preventDefault();
            $groups.val('');
            $ogs.val('');
            $usersList.find('tbody tr').show()
            var searchUser = e.target.value;

            if (searchUser.length < 3) {
                return;
            }

            $usersList.find('tbody tr').each(function() {
                var $td = $(this).find('td:eq(2)');
                var $li = $td.find('ul li');
                var match = false;

                $li.each(function() {
                    if ($(this).text().indexOf(searchUser) >= 0) {
                        match = true;
                    }
                });

                if (!match) {
                    $td.parent().hide();
                }
            });
        });
    }

    $.extend(Team.UsersOGs, {
        init: init
    });

})(window, jQuery);
