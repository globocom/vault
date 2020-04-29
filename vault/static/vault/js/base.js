var Base = Base || {};


Base.init = function() {
    Base.SubContent.init();
    Base.SetProject.init();
};


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
        $(".show_hide_password a").on('click', function(event) {
          event.preventDefault();
          let $input = $(this).parents(".show_hide_password").find("input");
          let $icon = $(this).parents(".show_hide_password").find("i");
          if($input.attr("type") == "text"){
            $input.attr('type', 'password');
            $icon.addClass( "fa-eye-slash" );
            $icon.removeClass( "fa-eye" );
          }else if($input.attr("type") == "password"){
            $input.attr('type', 'text');
            $icon.removeClass( "fa-eye-slash" );
            $icon.addClass( "fa-eye" );
          }
        });
    }

    $.extend(Base.Forms, {
        init: init
    });

})(window, jQuery);


Base.Messages = {};

(function(window, $) {
    'use strict';

    var msg_tmpl = ['<li>',
                        '<span class="msg">',
                            '<span class="msg-type-color"></span>',
                            '<span class="text"></span>',
                            '<a class="close-btn">',
                                '<i class="icon fa fa-times"></i>',
                            '</a>',
                        '</span>',
                    '</li>'].join('');

    function bindEvents() {
        $('.messages').on('click', '.close-btn', function() {
            $(this).closest('li').remove();
        });
    }

    function setMessage(options, fn) {
        if (typeof(fn) !== 'function') {
            fn = function () {};
        }

        var opts = $.extend({
            type: '',
            description: '',
            fixed: false
        }, options);

        var $messages = $('.messages'),
            $msg = $(msg_tmpl);

        if (opts.description === '') {
            return false;
        }

        $msg.hide().find('.text').html(opts.description);

        if (opts.type !== '') {
            $msg.addClass(opts.type);
        }

        $messages.append($msg);
        $msg.fadeIn('fast');

        if (!opts.fixed) {
            $msg.delay(5000).fadeOut('fast', function() {
                $(this).remove();
                fn();
            });
        }

        $('.messages').on('click', '.close-btn', function() {
            $(this).closest('li').remove();
            fn();
        });

        return $msg;
    }

    $.extend(Base.Messages, {
        setMessage: setMessage
    });

    $(document).ready(function() {
        bindEvents();
    });

})(window, jQuery);


Base.Paginator = {};

(function(window, $) {
    'use strict';

    var $page_number, $query_term;

    function init() {
        $page_number = $('#pag_number');
        let query_params = location.search.substring(1).split('&');
        $query_term = query_params.filter((e) => !e.startsWith('page')).join('&');
        bindEvents();
    }

    function bindEvents() {
        $page_number.keypress(function(event) {
            if (event.which == 13) {
                if($query_term == ''){
                    window.location=window.location.origin + window.location.pathname + '?page=' + $page_number.val()
                } else {
                    window.location=window.location.origin + window.location.pathname + '?page=' + $page_number.val() + '&' + $query_term
                }
            }
        });
    }

    $.extend(Base.Paginator, {
        init: init
    });

})(window, jQuery);


Base.SubContent = {};

(function(window, $) {
    'use strict';

    var $subContent, $closeBtn, $fullBtn,
        subContentHtml = ['<div id="sub-content">',
                            '<button class="close-btn"><i class="fa fa-times"></i></button>',
                            '<button class="full-btn">',
                                '<i class="max fa fa-expand"></i><i class="min fa fa-compress"></i>',
                            '</button>',
                            '<h4 class="sub-content-name"></h4>',
                            '<div class="inner"></div>',
                          '</div>'].join('');

    function init() {
        $subContent = $(subContentHtml);
        $('body').append($subContent);
        $closeBtn = $subContent.find('.close-btn');
        $fullBtn = $subContent.find('.full-btn');
        bindEvents();
    }

    function bindEvents() {
        $closeBtn.on('click', function() {
            close();
        });

        $fullBtn.on('click', function() {
            toggleFullscreen();
        });

        $(document).on('keyup', function(e) {
            if (e.keyCode == 27) {
                close();
            }
        });
    }

    function _clean() {
        $subContent.find('.inner').empty();
    }

    function fill(html) {
        $subContent.find('.inner').html(html);
    }

    function open(title, html) {
        if (title !== undefined) {
            setTitle(title);
        }
        if (html !== undefined) {
            fill(html);
        }
        $subContent.addClass('open');
    }

    function toggleFullscreen() {
        if($subContent.hasClass('fullscreen')) {
            $subContent.removeClass('fullscreen');
        } else {
            $subContent.addClass('fullscreen');
        }
    }

    function close() {
        _clean();
        $subContent.removeClass('open fullscreen');
    }

    function setTitle(title) {
        $subContent.find('.sub-content-name').text(title);
    }

    $.extend(Base.SubContent, {
        init: init,
        fill: fill,
        open: open,
        close: close,
        setTitle: setTitle,
        toggleFullscreen: toggleFullscreen
    });

})(window, jQuery);


Base.SetProject = {};

(function(window, $) {
    'use strict';

    var options, projectsHtml, $changeProject;

    function init(opts) {
        options = $.extend({
            'title': 'Select a project'
        }, opts);

        projectsHtml = $('.content-select-project').html();
        $changeProject = $('.btn-change-project');

        bindEvents();
    }

    function bindEvents() {
        $changeProject.on('click', function() {
            _openProjects();
        });
    }

    function _openProjects() {
        Base.SubContent.open(options.title, projectsHtml);
    }

    $.extend(Base.SetProject, {
        init: init
    });

})(window, jQuery);


Base.Cookie = {};

(function(window, $) {
    'use strict';

    function create(name, value, days) {
        if (days) {
            var date = new Date();
            date.setTime(date.getTime()+(days*24*60*60*1000));
            var expires = "; expires="+date.toGMTString();
        }
        else var expires = "";
        document.cookie = name+"="+value+expires+"; path=/";
    }

    function read(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for (var i=0; i<ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
    }

    function erase(name) {
        Base.Cookie.create(name, "", -1);
    }

    $.extend(Base.Cookie, {
        create: create,
        read: read,
        erase: erase
    });

})(window, jQuery);


Base.CSRF = {};

(function(window, $) {
    'use strict';

    function fix() {
        var csrftoken = Base.Cookie.read('csrftoken');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!_csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }

    function _csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.extend(Base.CSRF, {
        fix: fix
    });

})(window, jQuery);


Base.Loading = {};

(function(window, $) {
    'use strict';

    var appended = false;
    var loading_html = ['<div class="loading">',
                            '<div class="loading-content">',
                                '<i class="fas fa-spin fa-lg fa-cog"></i>',
                            '</div>',
                        '</div>'].join('');
    var $loading = $(loading_html);

    function show() {
        if (!appended) {
            $('body').append($loading);
            appended = true;
        }
        $loading.fadeIn();
    }

    function hide() {
        $loading.fadeOut('fast');
    }

    $.extend(Base.Loading, {
        show: show,
        hide: hide
    });

})(window, jQuery);


Base.Download = {};

(function(window, $) {
    'use strict';

    var fileTypes = {
        text: 'data:text/plain;charset=utf-8,',
        json: 'data:application/json;charset=utf-8,'
    }

    function text(fileName, text) {
        return _download(fileName, fileTypes.text, text);
    }

    function json(fileName, json) {
        return _download(fileName, fileTypes.json, json);
    }

    function _download(fileName, fileType, content) {
        var element = document.createElement('a');
        element.setAttribute('href', fileType + encodeURIComponent(content));
        element.setAttribute('download', fileName);

        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);
    }

    $.extend(Base.Download, {
        text: text,
        json: json
    });

})(window, jQuery);
