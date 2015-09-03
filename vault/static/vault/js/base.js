var Base = Base || {};


Base.Menu = {};

(function(window, $) {
    'use strict';

    var $main;

    function init() {
        $main = $('#sidebar');
        setCurrent();
        bindEvents();
    }

    function bindEvents() {
        $main.on('click', '.group', function() {
            $(this).closest('li').toggleClass('open');
        });
    }

    function setCurrent() {
        var path = trimSlash(location.pathname);
        $main.find('a').each(function() {
            if ( trimSlash($(this).attr('href')) === path ) {
                $(this).addClass('current');
            }
        });
    }

    function trimSlash(str) {
        return str.slice(-1) === '/' ?
               str.substring(0, str.length - 1) :
               str;
    }

    $.extend(Base.Menu, {
        init: init
    });

})(window, jQuery);


Base.Forms = {};

(function(window, $) {
    'use strict';

    var $delete_btn, options;

    function init(opts) {
        options = $.extend({
            'form_class': '.form-box',
            'delete_btn_class': '.delete-btn',
            'delete_msg': 'Confirm delete?'
        }, opts);

        $delete_btn = $(options.delete_btn_class);

        _bindEvents();
    }

    function _bindEvents() {
        $delete_btn.on('click', function() {
            if(window.confirm(options.delete_msg)) {
                window.location.href = $(this).attr('href');
            }
            return false;
        });
    }

    $.extend(Base.Forms, {
        init: init
    });

})(window, jQuery);


Base.Messages = {};

(function(window, $) {
    'use strict';

    function bindEvents() {
        $('.messages').on('click', '.close-btn', function() {
            $(this).closest('li').remove();
        });
    }

    function show(msg, cls) {
        var $container = $('.messages'),
            $msg = $(['<li>',
                        '<span class="msg">',
                          '<span class="text"></span>',
                          '<a class="close-btn">',
                            '<i class="icon fa fa-times"></i>',
                          '</a>',
                        '</span>',
                      '</li>'].join(''));

        $msg.hide()
            .find('.text')
            .text(msg);

        if (cls !== undefined) {
            $msg.addClass(cls);
        }

        $container.append($msg);

        $msg.fadeIn('fast')
            .delay(8000)
            .fadeOut('fast', function() {
                $(this).remove();
            });

        return $msg;
    }

    $.extend(Base.Messages, {
        show: show
    });

    $(document).ready(function() {
        bindEvents();
    });

})(window, jQuery);


Base.Util = {};

(function(window, $) {
    'use strict';

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $.extend(Base.Util, {
        getCookie: getCookie
    });

})(window, jQuery);


Base.SelectProject = {};

(function(window, $) {
    'use strict';

    var $main, $items, $current, $currentItem, project_id;

    function init(id) {
        project_id = id;

        // $main = $('#header .current-project');
        $main = $('.selectproject');
        $current = $main.find('.current');
        $currentItem = $main.find('[data-project-id="'+ project_id +'"]');

        bindEvents();
        // loadCurrentProject();
    }

    function bindEvents() {
        $main.on('click', '.set-project', function() {
            window.location.href = '/set-project/'+ $(this).data('project-id') + '?next=' + window.location.pathname;
        });
    }

    function loadCurrentProject() {
        $current.data('project-id', project_id)
                .find('.name')
                .text($currentItem.text());
    }

    $.extend(Base.SelectProject, {
        init: init
    });

})(window, jQuery);


Base.Metatada = {};

(function(window, $) {
    'use strict';

    var $meta, $btnMeta, $btnCloseMeta, $objName, $items, $tabs,
        $tabsContent, $objContent;

    function init() {
        $meta = $('.metadata');
        $btnMeta = $('.btn-meta');
        $btnCloseMeta = $meta.find('.close-meta-btn');
        $objName = $meta.find('.object-name');
        $items = $meta.find('.items');
        $tabs = $meta.find('.tabs-nav .tab');
        $tabsContent = $meta.find('.tabs-content .content');
        $objContent = $meta.find('.object-content');

        bindEvents();
    }

    function bindEvents() {
        $btnMeta.on('click', function() {
            showMetaInfo( $(this).data('name'), $(this).data('meta-url') );
            setObjContentUrl( $(this).data('download-url') );
        });

        $btnCloseMeta.on('click', function() {
            closeMeta();
        });

        $tabs.on('click', function() {
            $tabs.removeClass('active');
            $(this).addClass('active');

            $tabsContent.removeClass('active')
                        .eq($(this).index())
                        .addClass('active');
        });

        $tabs.filter('.tabcontent').on('click', function() {
            $objContent.attr('src', $objContent.data('content-url'));
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
        $tabs.filter('.tabmeta').click();
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

    function setObjContentUrl(url) {
        $objContent.data('content-url', url)
                   .attr('src', 'about:blank');
    }

    $.extend(Base.Metatada, {
        init: init
    });

})(window, jQuery);


Base.Paginator = {};

(function(window, $) {
    'use strict';

    var $page_number;

    function init() {
        $page_number = $('#pag_number');
        bindEvents();
    }

    function bindEvents() {
        $page_number.on('keypress', function(e) {
            if (e.which == 13) {
                window.location=window.location.origin + window.location.pathname + '?page=' + $page_number.val();
            }
        });
    }

    $.extend(Base.Paginator, {
        init: init
    });

})(window, jQuery);
