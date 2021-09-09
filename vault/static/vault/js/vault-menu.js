const VaultMenu = (ENDPOINTS = []) => {
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

  return new Vue({
    el: "#sidebar-app-menus",
    components: {
      "menu-item": MenuItem,
    },
    data: {
      endpoints: ENDPOINTS,
      items: [],
      updated: [],
    },
    async created() {
      const cached = localStorage.getItem("vaultMenuApps");
      const updated = [];

      if (cached) {
        this.items = JSON.parse(cached);
      }

      for (const url of this.endpoints) {
        const item = await this.fetchInfo(url);
        item.opened = false;
        updated.push(item);
        if (!cached) {
          this.items.push(item);
        }
      }

      localStorage.setItem("vaultMenuApps", JSON.stringify(updated));
    },
    methods: {
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
      </ul>
    `,
  });
};
