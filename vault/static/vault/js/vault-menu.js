const VaultMenu = (endpointsUrl = "/apps/info", projectId = "001") => {
  const CACHEKEY = `vMenuApp_${projectId}`;

  const SubMenuItem = {
    props: ["subitem"],
    template: `
    <li>
      <a :href="subitem.url" :title="subitem.name">{{ subitem.name }}</a>
    </li>
    `,
  };

  const MenuItem = {
    components: {
      "sub-menu-item": SubMenuItem,
    },
    props: ["item"],
    computed: {
      hasSub() {
        return this.item.subitems?.length > 0;
      },
    },
    methods: {
      toggleSubMenu(event) {
        if (this.hasSub) {
          event.preventDefault();
        }
        this.item.opened = !this.item.opened;
      },
    },
    template: `
    <li :class="{'submenu-active': item.opened}">
      <a class="app-main-menu-item" :class="{ 'dropdown-toggle': hasSub }"
         @click="toggleSubMenu"
         :href="item.url"
         :title="item.name">
        <i :class="['icon', item.icon]"></i> {{ item.name }}
      </a>
      <ul v-if="hasSub" class="sub-menu">
        <sub-menu-item v-for="(subitem, index) in item.subitems"
                       :subitem="subitem"
                       :key="'s'+index">
        </sub-menu-item>
      </ul>
    </li>
    `,
  };

  const DummyMenuItem = {
    template: `
    <li class="dummy-menu-item">
      <span>&nbsp;</span>
    </li>
    `,
  };

  return new Vue({
    el: "#sidebar-app-menus",
    components: {
      "menu-item": MenuItem,
      "dummy-menu-item": DummyMenuItem,
    },
    data: {
      loading: false,
      items: [],
      updated: [],
    },
    async created() {
      const cached = localStorage.getItem(CACHEKEY);
      this.updated = [];
      this.loading = true;

      if (cached) {
        this.items = JSON.parse(cached);
        this.loading = false;
      }

      let endpoints = [];

      try {
        endpoints = await this.fetchEndpoints();
      } catch (err) {
        console.log(err);
      }

      for (const url of endpoints) {
        try {
          const item = await this.fetchInfo(url);
          item.opened = false;
          this.updated.push(item);
          if (!cached) {
            this.items.push(item);
          }
        } catch (err) {
          console.log(err);
          continue;
        }
      }

      localStorage.setItem(CACHEKEY, JSON.stringify(this.updated));
      this.loading = false;
    },
    methods: {
      async fetchEndpoints() {
        const res = await fetch(endpointsUrl);
        return res.json();
      },
      async fetchInfo(url) {
        const res = await fetch(`${url}?opt=menu`);
        return res.json();
      },
    },
    template: `
      <ul class="app-menus">
        <menu-item v-for="(item, index) in items"
                   :item="item"
                   :key="'i'+index">
        </menu-item>
        <dummy-menu-item v-show="loading"></dummy-menu-item>
      </ul>
    `,
  });
};
