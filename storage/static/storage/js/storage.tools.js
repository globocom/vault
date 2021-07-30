var Storage = Storage || {};


Storage.Tools = {};

(function(window, $) {
    'use strict';

    var options, $tools, $btn_trash, $content, $opaque, $trash_modal, $btn_backup_restore,
        item_tmpl = ['<tr>',
                       '<td></td>',
                       '<td><%=name%></td>',
                       '<td><%=size%></td>',
                       '<td>',
                         '<a class="btn btn-sm btn-default btn-restore" title="Restore object"',
                           'data-toggle="tooltip" data-placement="left" data-object-name="<%=name%>" data-object-new-name="">',
                           '<i class="fa fa-download"></i>',
                         '</a>',
                       '</td>',
                     '</tr>'].join('');

    function init(opts) {
        options = $.extend({
            'deleted_objects_url': '',
            'restore_object_url': '',
            'trash_remove_url': '',
            'backup_restore_url': '',
            'container_name': '',
            'project_name': ''
        }, opts);

        $tools = $('#storage-tools');
        $btn_trash = $tools.find('.btn-trash');
        $content = $('.table-content');
        $opaque = $('.opaque');
        $trash_modal = $("#trash-modal");
        $btn_backup_restore = $(".backup-restore-buttons");

        Base.CSRF.fix();
        bindEvents();
    }

    function bindEvents() {
        $btn_trash.on('click', function() {
            _reset_content();
            _reset_modal();
            _populate_content();
        });

        _build_bind_restore_button();
        _bind_backup_restore_buttons();
    }

    function _build_bind_restore_button() {
       $content.on('click', '.btn-restore', function() {
            $('.btn-restore').addClass('disabled');
            $(this).addClass('active');
            _show_opaque();
            if ($(this).data('object-new-name') && $(this).data('object-new-name') != '' ){
                _restore_object($(this), $(this).data('object-name'), $(this).data('object-new-name'));
            } else {
                _restore_object($(this), $(this).data('object-name'), '');
            }
        });
    }

    function _bind_backup_restore_buttons() {
        $btn_backup_restore.on('click', '.btn-backup-restore-daily', function() {
            _run_backup_restore('daily');
        });
        $btn_backup_restore.on('click', '.btn-backup-restore-weekly', function() {
            _run_backup_restore('weekly');
        });
        $btn_backup_restore.on('click', '.btn-backup-restore-monthly', function() {
            _run_backup_restore('monthly');
        });
    }

    function _run_backup_restore(backup_type) {
        $('#backup-modal').find('button.close').click();
        Base.Loading.show();
        $.ajax({
            type: "POST",
            url: options.backup_restore_url,
            data: {
                'container': options.container_name,
                'project_name': options.project_name,
                'backup_type': backup_type
            }
        })
        .done(function (data) {
            Base.Loading.hide();
            Base.Messages.setMessage({
                description: data.message,
                type: 'success'
            });
        })
        .fail(function (data) {
            Base.Loading.hide();
            Base.Messages.setMessage({
                description: data.responseJSON.message,
                type: 'error'
            });
        });
    }

    function _show_opaque() {
        $opaque.show();
        $('#trash-modal .table').addClass('blurred');
    }

    function _hide_opaque() {
        $opaque.hide();
        $('#trash-modal .table').removeClass('blurred');
    }

    function _reset_content() {
        $content.html(['<tr>',
                         '<td colspan="4" style="text-align: center">',
                           '<div class="loader"></div>',
                         '</td>',
                       '</tr>'].join(''));
    }

    function _populate_content() {
        $.ajax({
            type: "GET",
            url: options.deleted_objects_url,
        })
        .done(function (data) {
            var objs = data.deleted_objects,
                content = "";

            options = $.extend({
                'original_container': data.original_container,
                'trash_container': data.trash_container
            }, options);

            for(var i=0, l=objs.length; i<l; i++) {
                content += tmpl(item_tmpl, objs[i]);
            }

            if(content !== "") {
                $content.html(content);
            } else {
                $content.html(['<tr>',
                                 '<td style="text-align:center;" colspan="4">',
                                   '<strong>0 Items</strong>',
                                 '</td>',
                               '</tr>'].join(''));
            }

            $('[data-toggle="tooltip"]').tooltip({'animation': false});
        })
        .fail(function (data) {
            _reset_modal();
            Base.Messages.setMessage({
                description: 'Error retrieving deleted items',
                type: 'error'
            });
        });
    }

    function _restore_object(register, name, new_name) {
        _show_hide_warning_msg('Hide');
        $.ajax({
            type: "POST",
            url: options.restore_object_url,
            data: {
                'container': options.original_container,
                'trash_container': options.trash_container,
                'object_name': name,
                'object_new_name': new_name
            }
        })
        .done(function (data) {
            _remove_from_trash(name);
        })
        .fail(function (data) {
            _check_status_code(register, data);
        });
    }

    function _remove_from_trash(name) {
        $.ajax({
            type: "POST",
            url: options.trash_remove_url,
            data: {
                'trash_container': options.trash_container,
                'object_name': name
            }
        })
        .done(function (data) {
            window.location.reload();
        })
        .fail(function (data) {
            _reset_modal();
            Base.Messages.setMessage({
                description: 'Error when trying to remove object from trash',
                type: 'error'
            });
        });
    }

    function _reset_modal() {
        $('#trash-modal').modal('hide');
        _show_hide_warning_msg('Hide');
        _hide_opaque();
    }

    function _reload_modal_for_object_already_exists_in_container(data) {
        $('.alert-warning').css('display', 'flex');
        $('.alert-warning').show();

        _update_result_table(data);
        _show_hide_warning_msg('Show');
        _update_data_restore_button(data.responseJSON["new_object_name"]);
    }

    function _bind_edit_new_name_object_value(table_cell_for_object_new_name_value) {
        $(table_cell_for_object_new_name_value).click(function () {
            var original_content = $(this).text();

            $(this).addClass("cell_editing");
            $(this).html("<input type='text' value='" + original_content + "' size='50'/>");
            $(this).children().first().focus();

            $(this).children().first().keypress(function (e) {
                if (e.which == 13) {
                    var newcontent = $(this).val();
                    _update_data_restore_button(newcontent);
                    $(this).parent().text(newcontent);
                    $(this).parent().removeClass("cell_editing");
                    _show_hide_warning_msg('Hide')
                }
            });

            $(this).children().first().blur(function(){
                $(this).parent().text(original_content);
                $(this).parent().removeClass("cell_editing");
                _show_hide_warning_msg('Hide')
            });
        });
    }

    function _update_result_table(data){
        var new_object_name = data.responseJSON["new_object_name"];
        var original_object_name = data.responseJSON["original_object_name"];

        $(".table-content tr").each(function(i, row) {
            var table_object_original_title = $trash_modal.find('tr th')[0];
            var $row = $(row);

            $(table_object_original_title).removeAttr("style");
            table_object_original_title.innerText = 'Nome Original';

            if ($row.find('td')[1].innerText != original_object_name) {
                // Recuperando / editando valores da tabela
                $row.find('td')[0].innerText = $row.find('td')[1].innerText;
                $row.find('td')[1].innerText = '-';
            } else {
                var table_object_new_name_title = $trash_modal.find("tr th")[1];

                // Recuperando / editando valores da tabela
                $row.find('td')[0].innerText = original_object_name;
                $row.find('td')[1].innerText = new_object_name;

                _bind_edit_new_name_object_value($row.find('td')[1]);

                table_object_new_name_title.innerText = "Nome Sugerido [Caso precise clique no novo nome para edicao]";

                // Destaca a linha a ser editada...
                $row.find('td')[0].style.color="#428bca";
                $row.find('td')[1].style.color="#428bca";
                $row.find('td')[2].style.color="#428bca";
            }
        });
    }

    function _check_status_code(register, data) {
        if(data.status==409) {
            _hide_opaque();
            _reload_modal_for_object_already_exists_in_container(data);
            return true;
        } else {
            Base.Messages.setMessage({
                description: 'Error when trying to restore object',
                type: 'error'
            });
            return false;
        }
    }

    function _update_data_restore_button(new_name){
        $('.btn-restore').removeClass('disabled');
        $(".btn-restore").data("object-new-name", new_name);
        _show_hide_warning_msg('Show')
    }

    function _show_hide_warning_msg(action) {
        if (action == 'Show') {
            $trash_modal.find(".error-msg").show();
            $('.alert-warning').show();
        }

        if (action == 'Hide') {
            $trash_modal.find(".error-msg").hide();
            $('.alert-warning').hide();
        }
    }

    $.extend(Storage.Tools, {
        init: init
    });

})(window, jQuery);


Storage.Container = {};

(function(window, $) {
    'use strict';

    var containerId, $btnOptions;

    function init() {
        $btnOptions = $('.btn-options');
        bindEvents();
        Base.CSRF.fix();
    }

    function bindEvents() {
        $btnOptions.on('click', function(e) {
            e.preventDefault();

            containerId = $(this).data('container-id');
            var $htmlContainerOptions = $('#html-'+ containerId).html();
            Base.SubContent.open('Container Options', $htmlContainerOptions);

            initOptionsActions();
        });
    }

    function initOptionsActions() {
        var $btnConfig = $('.config-item'),
            $btnDelete = $('.btn-delete-container');

        checkCurrentStatus();

        $btnConfig.on('click', function() {
            var $elem = $(this),
                url = $elem.data('setup-url'),
                current_status = $elem.data('current-status'),
                msgEnable = $elem.data('msg-enable'),
                msgDisable = $elem.data('msg-disable');

            if (current_status === 'disabled') {
                bootbox.confirm(msgEnable, function(result) {
                    result && sendUpdateContainer(url, 'enabled', $elem);
                });
            }

            if (current_status === 'enabled') {
                bootbox.confirm(msgDisable, function(result) {
                    result && sendUpdateContainer(url, 'disabled', $elem);
                });
            }
        });

        $btnDelete.on('click', function() {
            var $elem = $(this),
                msgDelete = $elem.data('msg-delete'),
                urlDelete = $elem.data('delete-url');

            bootbox.confirm(msgDelete, function(result) {
                result && deleteContainer(urlDelete);
            });
        });
    }

    function checkCurrentStatus() {
        var statusItems = $('#options-'+ containerId).data('status-urls');
        statusItems.map(function(item) {
            var $conf = $(item.elementId);

            if($conf.hasClass('enabled') || $conf.hasClass('disabled')) {
                return;
            }

            $.ajax({
                type: "GET",
                url: item.url,
            })
            .done(function(data) {
                if(data.status == 'enabled') {
                    $conf.data('current-status', 'enabled')
                         .removeClass('disabled')
                         .addClass('enabled');
                } else {
                    $conf.data('current-status', 'disabled')
                         .removeClass('enabled')
                         .addClass('disabled');
                }
            })
            .fail(function(data) {
                console.log(data);
            });
        });
    }

    function sendUpdateContainer(url, status, $elem) {
        Base.Loading.show();

        $.ajax({
            type: "GET",
            url: url,
            data: {'status': status}
        })
        .done(function (data) {
            $elem.removeClass('enabled disabled').addClass(status);
            $elem.data('current-status', status);

            Base.Loading.hide();
            var msg = data.responseJSON.message;
            if (msg !== '') {
                Base.Messages.setMessage({
                    description: msg,
                    type: 'success'
                });
                return;
            }

            window.location.reload();
        })
        .fail(function (data) {
            var msg = data.responseJSON.message;
            Base.Messages.setMessage({
                description: msg,
                type: 'error'
            });
            console.log(msg);
            Base.Loading.hide();
        });
    }

    function deleteContainer(url) {
        Base.Loading.show();

        $.ajax({
            type: 'DELETE',
            url: url
        })
        .done(function(data) {
            Base.Loading.hide();
            Base.Messages.setMessage({
                description: data.message,
                type: 'success'
            }, function() {
                window.location.reload();
            });
        })
        .fail(function(data) {
            Base.Messages.setMessage({
                description: data.message,
                type: 'fail'
            }, function() {
                window.location.reload();
            });
        });
    }

    $.extend(Storage.Container, {
        init: init
    });

})(window, jQuery);


Storage.Object = {};

(function(window, $) {
    'use strict';

    var $btnCustomMetadata, $tableCustomMetadata, $btnSave, row, customMetadata;

    function init() {
        $btnCustomMetadata = $('.btn-custom-metadata');
        $tableCustomMetadata = $('.table-custom-metadata');
        $btnSave = $('.btn-save');
        customMetadata = {};
        row = ['<tr>',
                    '<td>',
                        '<div style="display: flex; align-items: center; justify-content: space-around;">',
                            '<span style="width: 80%;">x-object-meta-</span>',
                            '<input type="text" class="form-control" value="" />',
                        '</div>',
                    '</td>',
                    '<td>',
                        '<div style="display: flex; align-items: center; justify-content: space-around;">',
                            '<input type="text" class="form-control" value="" />',
                            '<i class="fa fa-trash-alt" style="width: 1%;margin: 8px;"></i>',
                        '</div>',
                    '</td>',
                '</tr>'].join('');

        bindEvents();
        Base.CSRF.fix();
    }

    function bindEvents() {
        $btnCustomMetadata.on('click', function(e) {
            e.preventDefault();
            _add_new_header()
        });

        $btnSave.on('click', function(e) {
            e.preventDefault();
            _save()
        });

        $(document).on('click', '.fa-trash-alt', function(e) {
            e.preventDefault();
            _remove($(this));
        });
    }

    function _add_new_header() {
        var $tbody = $tableCustomMetadata.find('tbody');
        $tbody.append(row);
    }

    function _save() {
        var url = $tableCustomMetadata.data('custom-meta-url');
        var $tbody = $tableCustomMetadata.find('tbody');

        $tbody.find('tr').each(function(index, tr) {
            var $td = $(tr).find('td');
            var key = $($td[0]).find('input').val();
            var value = $($td[1]).find('input').val();
            if ($.trim(key) !== '') {
                var slug = _convert_to_slug(key);
                customMetadata['x-object-meta-' + slug] = value;
                $($td[0]).find('input').val(slug);
            }
        });

        $.ajax({
            type: 'POST',
            url: url,
            data: customMetadata
        })
        .done(function (data) {
            Base.Messages.setMessage({
                description: data.message,
                type: 'success'
            });
        })
        .fail(function (data) {
            Base.Messages.setMessage({
                description: data.message,
                type: 'error'
            });
        });
    }

    function _remove(object) {
        var $tr = object.parents('tr');
        var $td = $tr.find('td:first');
        var value = $td.find('input').val();
        delete customMetadata[value];
        $tr.remove();
    }

    function _convert_to_slug(text) {
        return $.trim(text)
            .toLowerCase()
            .replace(/[^\w ]+/g,'')
            .replace(/ +/g,'-');
    }

    $.extend(Storage.Object, {
        init: init
    });

})(window, jQuery);
