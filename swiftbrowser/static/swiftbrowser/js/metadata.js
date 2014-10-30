Metatada = {};

(function(window, $) {
    'use strict';

    var $meta, $items, $objName, $btnMeta, $btnCloseMeta;

    function init() {
        $meta = $('.metadata');
        $btnMeta = $('.btn-meta');
        $btnCloseMeta = $meta.find('.close-btn');
        $objName = $meta.find('.object-name');
        $items = $meta.find('.items');

        bindEvents();
    }

    function bindEvents() {
        $btnMeta.on('click', function() {
            showMetaInfo( $(this).data('name'), $(this).data('meta-url') );
        });

        $btnCloseMeta.on('click', function() {
            closeMeta();
        });

        $(document).on('keyup', function(e) {
            if (e.keyCode == 27) {
                closeMeta();
            }
        });
    }

    function closeMeta() {
        $meta.removeClass('open');
        $objName.text('');
        $items.html('');
    }

    function showMetaInfo(name, url) {
        var lts = '';

        $meta.addClass('open');
        $objName.text(name)
                .attr('title', name);

        $.ajax({
            type: "GET",
            url: url
        })
        .done(function (data) {
            for(var item in data) {
                if (data.hasOwnProperty(item)) {
                    lts += ['<li>',
                              '<span class="key"><i class="fa fa-caret-right"></i>&nbsp;'+ item +'</span>',
                              '<span class="value">'+ data[item] +'</span>',
                            '</li>'].join('');
                }
            }
            $items.html(lts);
        })
        .fail(function (data) {
            Base.Messages.show("Unable to show item metadata" , 'error');
        });
    }

    $.extend(Metatada, {
        init: init
    });

})(window, jQuery);
