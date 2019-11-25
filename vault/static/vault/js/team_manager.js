var TeamManager = TeamManager || {};

(function(window, $) {
    'use strict';

    var options, $main, $addBtn, $removeBtn, $modal, $usersSelect;

    function init(opts) {
        options = $.extend({
            'addUrl': '',
            'deleteUrl': '',
            'listUrl': ''
        }, opts);

        $main = $('.team-manager');
        $addBtn = $main.find('.btn-add-user');
        $removeBtn = $main.find('.btn-remove-user');
        $modal = $('#add_user_modal');

        if (!TeamManager.called) {
            bindEvents();
            TeamManager.called = true;
        }

        Base.CSRF.fix();
    }

    function bindEvents() {
        $addBtn.on('click', function(e) {
            e.preventDefault();
            var id = $(this).data('group-id'),
                name = $(this).data('group-name');

            fillModal(id, name);
        });

        $removeBtn.on('click', function(e) {
            e.preventDefault();
            var groupId = $(this).data('group-id'),
                userId = $(this).data('user-id');

            alert(groupId + ', ' + userId);
        });
    }

    function fillModal(groupId, groupName) {
        var $usersSelect = $modal.find('.modal-users'),
            $modalName = $modal.find('.modal-team-name'),
            $modalGroupId = $modal.find('.modal-group-id');

        $modalName.text(groupName);
        $modalGroupId.val(groupId);

        $.ajax({
            url: options.outsideUserstUrl +'?group='+ groupId
        })
        .done(function (data) {
            console.log(data);
        })
        .fail(function (data) {
            Base.Messages.setMessage({
                description: data.responseJSON.msg,
                type: 'error'
            });
        });
    }

    $.extend(TeamManager, {
        called: false,
        init: init
    });

})(window, jQuery);
