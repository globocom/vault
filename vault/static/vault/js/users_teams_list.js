var Team = Team || {};


Team.Users = {};

(function(window, $) {
    'use strict';

    var $main, $groups, $users, $usersList;

    function init() {
        $main = $('#search-user-team');
        $groups = $main.find('.groups');
        $users = $main.find('.users');
        $usersList = $main.find('.related-users');

        bindEvents();
    }

    function bindEvents() {
        $groups.on('change', function(e) {
            e.preventDefault();
            $users.val('');
            $usersList.find('tbody tr').show()
            var searchGroup = this.options[e.target.selectedIndex].text;

            if (this.options[e.target.selectedIndex].value === 'All') {
                return;
            }

            $usersList.find('tbody tr').each(function() {
                var group = $(this).find('td:first').text();
                if (searchGroup !== group) {
                    $(this).hide()
                }
            });
        });

        $users.on('keyup', function(e) {
            e.preventDefault();
            $groups.val('');
            $usersList.find('tbody tr').show()
            var searchUser = e.target.value;

            if (searchUser.length < 3) {
                return;
            }

            $usersList.find('tbody tr').each(function() {
                var $td = $(this).find('td:eq(1)');
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

    $.extend(Team.Users, {
        init: init
    });

})(window, jQuery);
