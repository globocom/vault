var Metadata = Metadata || {};

(function(window, $) {
    'use strict';

    var options, $btnMeta, $btnPreview;

    function init(opts) {
        options = $.extend({
            'showPreview': true
        }, opts);

        $btnMeta = $('.btn-meta');
        $btnPreview = $('<a href="#" target="_blank" class="btn-preview btn btn-xs btn-primary">preview</a>');

        bindEvents();
    }

    function bindEvents() {
        $btnMeta.on('click', function() {
            showMetaInfo($(this).data('sub-content-title'),
                         $(this).data('name'),
                         $(this).data('meta-url'));
            $btnPreview.attr('href', $(this).data('preview-url'));
        });
    }

    function fillContent(name, items) {
        var content = [
            '<span class="obj-name" title="'+ name +'">'+ name +'</span>',
            '<ul class="metadata-items">'+ items +'</ul>'
        ].join('');

        var $container = $('<div class="metadata"></div>');

        if (options.showPreview) {
            $container.append($btnPreview);
        }

        $container.append(content);
        Base.SubContent.fill($container);
    }

    function showMetaInfo(title, name, url) {
        Base.SubContent.open(title);

        $.ajax({
            type: "GET",
            url: url
        })
        .done(function (data) {
            var items = '';

            for(var i in data) {
                if (data.hasOwnProperty(i)) {
                    items += '<li><span class="key">'+ i +':</span><span class="value">'+ data[i] +'</span></li>';
                }
            }

            fillContent(name, items);
        })
        .fail(function (data) {
            Base.Messages.setMessage({
                description: 'Unable to show item metadata',
                type: 'error'
            });
        });
    }

    $.extend(Metadata, {
        init: init
    });

})(window, jQuery);


Metadata.CacheControl = {};

(function(window, $) {
    'use strict';

    var $btnCacheControl, $formCacheControl, $btnSend,
        cacheUrl = '';

    function init() {
        $btnCacheControl = $('.btn-cache-control');
        $formCacheControl = $('#form-cache-control');
        $btnSend = $('.btn-send-cache');

        Base.CSRF.fix();
        bindEvents();
    }

    function bindEvents() {
        $btnCacheControl.on('click', function() {
            cacheUrl = $(this).data('cache-control-url');
            console.log(cacheUrl);
        });

        $btnSend.on('click', function(e) {
            e.preventDefault();
            if(!$(this).hasClass('waiting')) {
                sendCacheControl(cacheUrl);
            }
        });
    }

    function sendCacheControl(cacheUrl) {
        var days = $formCacheControl.find('input[name=days]').val();
        $btnSend.addClass('waiting');

        $.ajax({
            type: 'POST',
            url: cacheUrl,
            data: {'days': days}
        })
        .done(function (data) {
            Base.Messages.setMessage({
                description: data.message,
                type: 'success'
            });
            $('#modal-cache-control').modal('hide');
            $btnSend.removeClass('waiting');
        })
        .fail(function (data) {
            Base.Messages.setMessage({
                description: data.message,
                type: 'error'
            });
            $('#modal-cache-control').modal('hide');
            $btnSend.removeClass('waiting');
        });
    }

    $.extend(Metadata.CacheControl, {
        init: init
    });

})(window, jQuery);
