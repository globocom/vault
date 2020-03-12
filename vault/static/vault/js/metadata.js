var Metadata = Metadata || {};

(function(window, $) {
    'use strict';

    var options, $btnMeta, $btnPreview;

    function init(opts) {
        options = $.extend({
            'showPreview': true
        }, opts);

        $btnMeta = $('.btn-meta');
        $btnPreview = $('<a href="#" target="_blank" class="btn-preview btn btn-sm btn-primary">preview</a>');

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

    var options, $btnCacheControl, $formCacheControl, $btnSend, $inputMaxAge,
        cacheUrl = '';

    function init(opts) {
        options = $.extend({
            'callBack': null
        }, opts);

        $btnCacheControl = $('.btn-cache-control');
        $formCacheControl = $('#form-cache-control');
        $inputMaxAge = $formCacheControl.find('input[name=maxage]');
        $btnSend = $('.btn-send-cache');

        Base.CSRF.fix();
        bindEvents();
    }

    function bindEvents() {
        $btnCacheControl.on('click', function() {
            cacheUrl = $(this).data('cache-control-url');
            $formCacheControl.find('input[name=unit][value=minutes]').prop('checked', true);
            $inputMaxAge.val(3);
            getMetaInfo(cacheUrl.replace('cache-control', 'metadata'));
        });

        $btnSend.on('click', function(e) {
            e.preventDefault();
            var unit = $formCacheControl.find('input[name=unit]:checked').val();
            var maxage = $inputMaxAge.val();
            if(unit === 'minutes' && maxage < 3) {
                Base.Messages.setMessage({
                    description: 'O cache-control deve ter no mínimo 3 minutos',
                    type: 'error'
                });
                return;
            }
            if(!$(this).hasClass('waiting')) {
                sendCacheControl(cacheUrl);
            }
        });
    }

    function getMetaInfo(url) {
        $.ajax({
            type: "GET",
            url: url
        })
        .done(function (data) {
            for(var key in data) {
                if (key.toLowerCase() === 'cache-control') {
                    var cacheControl = data[key];
                    var regexp = /max-age=([0-9]+)/gi;
                    var match = regexp.exec(cacheControl);
                    $inputMaxAge.val(match[1] / 60);
                    break;
                }
            }
        })
        .fail(function (data) {
            Base.Messages.setMessage({
                description: 'Unable to show item metadata',
                type: 'error'
            });
        });
    }

    function sendCacheControl(cacheUrl) {
        var unit = $formCacheControl.find('input[name=unit]:checked').val();
        var maxage = $formCacheControl.find('input[name=maxage]').val();
        $btnSend.addClass('waiting');

        $.ajax({
            type: 'POST',
            url: cacheUrl,
            data: {
                'unit': unit,
                'maxage': maxage
            }
        })
        .done(function (data) {
            if (options.callBack) {
              options.callBack(data.cache_control)
            }
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
