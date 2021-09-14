const VaultDashboard = (endpointsUrl = "/apps/info", projectId = "001") => {
  const CACHEKEY = `vDash_${projectId}`;

  const DashboardWidget = {
    props: ["widget"],
    methods: {
      propBreak(index) {
        return (
          (this.widget.properties.length == 2 && index == 0) ||
          (index + 1) % 2 == 0
        );
      },
    },
    template: `
    <li class="col-md-6">
      <div :class="['box', 'widget', widget.name]">
        <div class="head" :style="{ backgroundColor: widget.color }">
          <span class="name">
            {{ widget.title }}
            <span class="info">{{ widget.subtitle }}</span>
          </span>
          <a class="extra-info" v-if="widget.extra" href="#" :title="widget.extra.title"
            data-bs-toggle="tooltip" data-placement="top">
            <span class="status">{{ widget.extra.status }}</span>
            <i :class="[widget.extra.icon]"></i>
          </a>
        </div>

        <div class="content">
          <template v-for="(prop, index) in widget.properties">
            <div class="item-box">
              {{ prop.description }}
              <span class="big-number">{{ prop.value }}</span>
              {{ prop.name }}
            </div>
            <div v-if="propBreak(index)" class="item-box-break"></div>
          </template>
        </div>

        <div class="base">
          <a class="btn btn-sm btn-light"
            v-for="(bt, index) in widget.buttons"
            :key="'b'+index"
            :href="bt.url">
            {{ bt.name }}
          </a>
        </div>
      </div>
    </li>
    `,
  };

  const DummyWidget = {
    template: `
    <li class="col-md-6">
      <div class="widget-dummy"></div>
    </li>
    `,
  };

  return new Vue({
    el: "#dashboard-widgets",
    components: {
      "dashboard-widget": DashboardWidget,
      "dummy-widget": DummyWidget,
    },
    data: {
      loading: false,
      widgets: [],
      updated: [],
    },
    async created() {
      const cached = localStorage.getItem(CACHEKEY);
      this.updated = [];
      this.loading = true;

      if (cached) {
        this.widgets = JSON.parse(cached);
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
          const [widget] = await this.fetchInfo(url);

          if (widget) {
            this.updated.push(widget);
          }

          if (!cached && widget) {
            this.widgets.push(widget);
          }
        } catch (err) {
          console.log(url);

          console.log(err);
          continue;
        }
      }

      localStorage.setItem(CACHEKEY, JSON.stringify(this.updated));
      this.loading = false;
      this.update();
    },
    methods: {
      async fetchEndpoints() {
        const res = await fetch(endpointsUrl);
        return res.json();
      },
      async fetchInfo(url) {
        const res = await fetch(`${url}?opt=widgets`);
        return res.json();
      },
      update() {
        this.widgets = this.updated;
        console.log("dashboard updated");
      },
    },
    template: `
    <ul class="row dashboard-widgets">
      <dashboard-widget v-for="(widget, index) in widgets"
                        :widget="widget"
                        :key="'w'+index">
      </dashboard-widget>
      <dummy-widget v-show="loading"></dummy-widget>
    </ul>
    `,
  });
};
