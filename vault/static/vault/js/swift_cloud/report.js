const ReportApp = {
  el: "#migration-report-app",
  data: {
    projects: PROJECTS,
    migrationData: MIGRATION_DATA,
    projectStatusUrl: PROJECT_STATUS_URL,
  },
  computed: {
    migrated() {
      return this.migrationData.filter((i) => i.final_date).length;
    },
    updatedProjects() {
      return this.projects.map((project) => {
        const data = this.migrationData.filter(
          (i) => i.project_id === project.id
        );

        project.status = "--";

        if (data.length) {
          projectData = data[0];

          project.status = "Waiting in migration queue";

          if (projectData.initial_date && !projectData.final_date) {
            project.status = "Migrating...";
          }

          if (projectData.final_date) {
            project.status = "Done";
          }
        }

        return project;
      });
    },
  },
  template: `
  <div class="box-table">
    <table class="table">
      <thead>
        <tr>
          <th width="30%">Project Name</th>
          <th width="30%">Project ID</th>
          <th>Migration Status</th>
          <th width="10%"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="project in updatedProjects" :key="project.id">
          <td>{{ project.name }}</td>
          <td>{{ project.id }}</td>
          <td>
            <span class="me-2">{{ project.status }}</span>
          </td>
          <td class="text-end">
            <a class="btn btn-sm btn-default" :href="projectStatusUrl + '?project_id=' + project.id">
              Details
            </a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  `,
};

new Vue(ReportApp);
