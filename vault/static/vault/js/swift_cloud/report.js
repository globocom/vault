// const reportData = Vue.observable({});

const ReportApp = {
  el: "#report-app",
  data: {
    projects: PROJECTS,
    statusUrl: STATUS_URL,
    migrateUrl: MIGRATE_URL,
  },
  created() {
    for (const project of this.projects) {
      this.getProjectStatus(project);
    }
  },
  methods: {
    async getProjectStatus(project) {
      const data = await fetch(`${this.statusUrl}?project_id=${project.id}`);
      const result = await data.json();
      project.status = result.status;
    },
    async migrateProject(project) {
      const csrfToken = Base.Cookie.read("csrftoken");
      const res = await fetch(this.migrateUrl, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          project_id: project.id,
          project_name: project.name,
          environment: project.environment,
        }),
      });
      const result = await res.json();

      if (!res.ok) {
        Base.Messages.setMessage({
          type: "error",
          description: result.error,
        });
        return;
      }

      Base.Messages.setMessage({
        type: "success",
        description: result.message,
      });

      this.getProjectStatus(project);
    },
  },
  template: `
  <div class="box-table">
    <table class="table">
      <thead>
        <tr>
          <th width="28%">ID</th>
          <th>Project Name</th>
          <th>Status</th>
          <th width="10%"></th>
          <th width="10%"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="project in projects" :key="project.name">
          <td>{{ project.id }}</td>
          <td>{{ project.name }}</td>
          <td>{{ project.status }}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-light" @click="getProjectStatus(project)">
              Update
            </button>
          </td>
          <td class="text-end">
            <button class="btn btn-sm btn-primary" @click="migrateProject(project)">
              Migrate
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  `,
};

new Vue(ReportApp);
