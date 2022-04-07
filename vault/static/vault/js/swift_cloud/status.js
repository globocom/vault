const StatusApp = {
  el: "#migration-status-app",
  data: {
    projects: PROJECTS,
    migrationData: MIGRATION_DATA,
    projectStatusUrl: PROJECT_STATUS_URL,
    trans: TRANSLATIONS,
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
          project.status = this.trans.waitingMigration;

          if (projectData.initial_date && !projectData.final_date) {
            project.status = this.trans.migrating;
          }

          if (projectData.final_date) {
            project.status = this.trans.migrationCompleted;
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
        {{ trans.totalProjects }}:<br />
        <strong class="fs-3">{{ projects.length }}</strong>
      </div>

      <div class="box me-4">
        {{ trans.migratedProjects }}:<br />
        <strong class="fs-3">{{ migrated }}</strong>
      </div>
    </div>

    <div class="box-table">
      <table class="table">
        <thead>
          <tr>
            <th width="30%">{{ trans.projectName }}</th>
            <th width="30%">{{ trans.projectId }}</th>
            <th>{{ trans.team }}</th>
            <th>{{ trans.migrationStatus }}</th>
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
                {{ trans.details }}
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
