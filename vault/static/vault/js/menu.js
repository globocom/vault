var VaultMenu = (function(window) {
  'use strict';

  var urls, options;

  function init(opts) {
    const query = "?opt=menu";

    var currentDate = new Date();
    var currentDateString = dateToString(currentDate);
    var cachedUrls = [];
    var contents = []

    options = Object.assign({
      'endpoints': null
    }, opts);

    urls = options.endpoints;

    urls.forEach(async (url) => {
      var cache = localStorage.getItem(url);

      if (cache && currentDateString <= JSON.parse(cache).expires) {
        let data = JSON.parse(cache).content;
        data.json_endpoint = url;
        renderMenuItem(data);
      } else {
        let response = await fetch(url + query);

        try {
          let data = await response.json();

          let expireDate = new Date(currentDate.getTime() + 5 * 60000);
          localStorage.setItem(url, JSON.stringify({
            "content": data,
            "expires": dateToString(expireDate)
          }));

          data.json_endpoint = url;
          renderMenuItem(data);

        } catch (err) {
          return;
        }

      }
    });
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
    let wid = document.createElement("li");

    wid.innerHTML = tmpl("menu_icon_default", Object.assign({
      "name": "default",
      "icon": "fas fa-question-circle",
      "url": "#"
    }, obj));

    wid.json_endpoint = obj.json_endpoint;

    let sidebar_menu = document.getElementById("sidebar-app-menus");

    let submenu = document.createElement("ul");
    submenu.classList.add('sub-menu');

    if ('subitems' in obj && obj.subitems.length > 0) {
      wid.firstElementChild.classList.add("dropdown-toggle");
      wid.firstElementChild.href = "#"

      obj.subitems.forEach(function(item) {
        let subitems = document.createElement("li");
        subitems.innerHTML = tmpl("submenu_icon_default", Object.assign({
          "name": "default",
          "icon": "fas fa-caret-right",
          "url": "#"
        }, item));
        submenu.appendChild(subitems)
      });

      wid.appendChild(submenu);

      wid.firstElementChild.addEventListener("click", function(e) {
        this.classList.toggle("sidebar-menu-active");
        if (submenu.style.maxHeight) {
          submenu.style.maxHeight = null;
        } else {
          submenu.style.maxHeight = submenu.scrollHeight + "px";
        }
      });
    }

    let sidebar_menu_items = Array.from(sidebar_menu.children);
    sidebar_menu_items.push(wid);
    sidebar_menu_items.sort(function(a, b) {
      return urls.indexOf(a.json_endpoint) - urls.indexOf(b.json_endpoint);
    });

    sidebar_menu.innerHTML = '';
    sidebar_menu_items.forEach(function(i) {
      sidebar_menu.appendChild(i);
    });
  }

  function renderSubMenuItem(obj) {}

  return {
    init: init
  };

})(window);
