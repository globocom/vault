const StatusApp = {
  el: "#migration-status-app",
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
  <div>
    <div class="d-flex justify-content-start">
      <div class="box me-4">
        Total projects:<br />
        <strong class="fs-3">{{ projects.length }}</strong>
      </div>

      <div class="box me-4">
        Migrated projects:<br />
        <strong class="fs-3">{{ migrated }}</strong>
      </div>
    </div>

    <div class="box-table">
      <table class="table">
        <thead>
          <tr>
            <th width="30%">Project Name</th>
            <th width="30%">Project ID</th>
            <th>Team</th>
            <th>Migration Status</th>
            <th width="10%"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="project in updatedProjects" :key="project.id">
            <td>
              <a :href="projectStatusUrl + '?project_id=' + project.id">
                {{ project.name }}
              </a>
            </td>
            <td>{{ project.id }}</td>
            <td>{{ project.team }}</td>
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
  </div>
  `,
};

new Vue(StatusApp);
