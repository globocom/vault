const reportData = Vue.observable({});

const ReportApp = {
  el: "#report-app",
  data: {
    projects: PROJECTS,
    defaultHeaders: {
      Accept: "application/json, text/plain, */*",
      "Content-Type": "application/json",
    },
  },
  methods: {
    getProjectStatus(projectId) {},
  },
  template: `
  <div class="box-table">
    <table class="table">
      <thead>
        <tr>
          <th width="25%">ID</th>
          <th>Project Name</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="project in projects" :key="project.name">
          <td>{{ project.id }}</td>
          <td>{{ project.name }}</td>
          <td></td>
          <td class="text-end">
            <button class="btn btn-sm btn-light">View</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  `,
};

new Vue(ReportApp);
