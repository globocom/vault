var VaultMenu = (function(window) {
  'use strict';

  var urls, options;

  function init(opts) {
    const execute = (url) => {
      return new Promise((resolve, reject) => {
        fetch(url, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        }).then((response) => {
          if(response.ok) {
            resolve(response.json());
          }
        }).catch(function(error) {
          resolve({});
        });
      })
    }
    const promises = []
    const query = "?opt=menu";

    var currentDate = new Date();
    var currentDateString = dateToString(currentDate);
    var cachedUrls = [];
    var contents = []

    options = Object.assign({
        'endpoints': null
    }, opts);

    urls = options.endpoints.sort();

    for (var i = 0; i < urls.length; i++) {
      var url = urls[i] + query;
      var cache = localStorage.getItem(url);

      if (cache && currentDateString <= JSON.parse(cache).expires) {
        cachedUrls.push(url);
        contents.push(JSON.parse(cache).content);
      }
    }

    let urlsNoCached = urls.filter(function(url) {
      return !cachedUrls.includes(url + query);
    }).sort();

    if (urlsNoCached.length === 0) {
      for (var i = 0; i < contents.length; i++) {
        renderMenuItem(contents[i]);
      }
      return;
    }

    for (var i = urls.length - 1; i >= 0; i--) {
      promises.push(execute(urls[i] + query));
    }

    Promise.all(promises).then((response) => {
      var responses = response.sort((a, b) => (a.name > b.name) ? 1 : -1);

      return responses.map(function(data, index) {
        var url = urls[index].replace(location.origin, '') + query;
        var cache = localStorage.getItem(url);

        if (!cache || JSON.parse(cache).expires <= currentDateString) {
          var expireDate = new Date(currentDate.getTime() + 5 * 60000);
          localStorage.setItem(url, JSON.stringify({
            "content": data,
            "expires": dateToString(expireDate)
          }));
        }
        renderMenuItem(data);
      });

    })
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

    var submenu = document.createElement("ul");
    submenu.classList.add('sub-menu');

    obj.subitems.forEach(function(item) {
      var subitems = document.createElement("li");
      subitems.innerHTML = tmpl("submenu_icon_default", Object.assign({
        "name": "default",
        "icon": "fas fa-caret-right",
        "url": "#"
      }, item));
      submenu.appendChild(subitems)
    });

    wid.appendChild(submenu);
  }

  function renderSubMenuItem(obj) {}

  return {
    init: init
  };

})(window);
