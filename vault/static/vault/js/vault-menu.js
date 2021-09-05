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
    props: ["item", "updateItem"],
    methods: {
      toggleSubMenu() {
        this.item.opened = !this.item.opened;
        this.updateItem(this.item);
      },
    },
    template: `
    <li :class="{'submenu-active': item.opened}">
      <a class="app-main-menu-item dropdown-toggle"
         @click.prevent="toggleSubMenu"
         :href="item.url"
         :title="item.name">
        <i :class="['icon', item.icon]"></i> {{ item.name }}
      </a>
      <ul v-if="item.subitems?.length" class="sub-menu">
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
    },
    async created() {
      const currentItems = localStorage.getItem("vaultMenuApps");

      if (currentItems) {
        this.items = JSON.parse(currentItems);
      }

      localStorage.setItem("vaultMenuApps", JSON.stringify([]));

      for (const url of this.endpoints) {
        const item = await this.fetchInfo(url);
        item.opened = false;
        this.updateItem(item);
      }
    },
    methods: {
      async fetchInfo(url) {
        const res = await fetch(`${url}?opt=menu`);
        return res.json();
      },
      updateItem(item) {
        if (!this.items.filter((i) => i.name == item.name).length) {
          this.items.push(item);
        }
        localStorage.setItem("vaultMenuApps", JSON.stringify(this.items));
      },
    },
    template: `
      <ul class="app-menus">
        <menu-item v-for="(item, index) in items"
                   :item="item"
                   :updateItem="updateItem"
                   :key="'i'+index">
        </menu-item>
      </ul>
    `,
  });
};
