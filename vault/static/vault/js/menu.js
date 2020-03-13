var VaultMenu = (function(window) {
  'use strict';

  var urls, options;

  function init(opts) {
    options = $.extend({
        'endpoints': null
    }, opts);

    urls = options.endpoints;

    var currentDate = new Date();
    var currentDateString = dateToString(currentDate);
    var cachedUrls = [];

    urls.forEach(function(u) {
      try {
        var cache = JSON.parse(localStorage.getItem(u + "?opt=menu"));
        if (cache.expires > currentDateString) {
          renderMenuItem(JSON.parse(cache.content));
          cachedUrls.push(u);
        }
      } catch (err) {
        // err
      }
    });

    urls = urls.filter(function(u) {
      return !cachedUrls.includes(u);
    });

    Promise.all(urls.map(function(u) {
      return fetch(u + "?opt=menu");
    }))
    .then(function(responses) {

      return responses.map(function(res) {
        var url = res.url.replace(location.origin, '');

        var text = res.text().then(function(data) {
          try {
            var jsonData = JSON.parse(data);
          } catch (err) {
            return;
          }

          var cache = localStorage.getItem(url);
          if (cache === null || JSON.parse(cache).expires <= currentDateString) {
            var expireDate = new Date(currentDate.getTime() + 5 * 60000);
            localStorage.setItem(url, JSON.stringify({
              "content": data,
              "expires": dateToString(expireDate)
            }));
          }

          renderMenuItem(jsonData);
        });
      })
    });

    Base.CSRF.fix();
  }

  function dateToString(date) {
    return date.getFullYear() + '-'
          + (date.getMonth() < 9 ? '0' : '')
          + (date.getMonth() + 1) + '-'
          + (date.getDate() < 10 ? '0' : '')
          + date.getDate() + ' '
          + (date.getHours() < 10 ? '0' : '')
          + date.getHours() + ':'
          + (date.getMinutes() < 10 ? '0' : '')
          + date.getMinutes() + ':'
          + (date.getSeconds() < 10 ? '0' : '')
          + date.getSeconds();
  }

  function renderMenuItem(obj) {
    var wid = document.createElement("li");
    wid.innerHTML = tmpl("menu_icon_default", Object.assign({
      "name": "default",
      "icon": "fas fa-question-circle",
      "url": "#"
    }, obj));

    var sidebar_menu = document.getElementById("sidebar-app-menus");
    sidebar_menu.appendChild(wid);
  }

  return {
    init: init
  };

})(window);
