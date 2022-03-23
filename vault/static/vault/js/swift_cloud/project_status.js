const ProjectStatusApp = {
  el: "#project-migration-status-app",
  data: {
    projectName: PROJECT_NAME,
    projectId: PROJECT_ID,
    metadata: METADATA,
    migrationData: MIGRATION_DATA,
    migrateUrl: MIGRATE_URL,
    removalUrl: REMOVAL_URL,
    projectStatus: PROJECT_STATUS,
    environ: ENVIRON,
  },
  computed: {
    hasMigrationData() {
      return this.migrationData.hasOwnProperty("project_id");
    },
    wasRemoved() {
      return this.metadata.hasOwnProperty("x-account-meta-cloud-remove");
    },
  },
  methods: {
    reset() {
      window.setTimeout(() => {
        Base.Loading.hide();
        window.location.reload();
      }, 1000);
    },
    async startMigration() {
      if (!window.confirm("This will start the migration. Confirm?")) {
        return;
      }

      Base.Loading.show();

      const csrfToken = Base.Cookie.read("csrftoken");
      const res = await fetch(this.migrateUrl, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          project_id: this.projectId,
          project_name: this.projectName,
          environment: this.environ,
        }),
      });
      const result = await res.json();

      if (!res.ok) {
        Base.Messages.setMessage({
          type: "error",
          description: result.error,
        });
        Base.Loading.hide();
        return;
      }

      Base.Messages.setMessage({
        type: "success",
        description: result.message,
      });

      this.reset();
    },
    async removeProject() {
      if (!window.confirm("The project will be marked for removal. Confirm?")) {
        return;
      }

      Base.Loading.show();

      const csrfToken = Base.Cookie.read("csrftoken");
      const res = await fetch(this.removalUrl, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ project_id: this.projectId }),
      });
      const result = await res.json();

      if (!res.ok) {
        Base.Messages.setMessage({
          type: "error",
          description: result.error,
        });
        Base.Loading.hide();
        return;
      }

      Base.Messages.setMessage({
        type: "success",
        description: result.message,
      });

      this.reset();
    },
    async undoRemoveProject() {
      if (
        !window.confirm("This will undo the removal of this project. Continue?")
      ) {
        return;
      }

      Base.Loading.show();

      const csrfToken = Base.Cookie.read("csrftoken");
      const res = await fetch(this.removalUrl, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          project_id: this.projectId,
          undo_removal: true,
        }),
      });
      const result = await res.json();

      if (!res.ok) {
        Base.Messages.setMessage({
          type: "error",
          description: result.error,
        });
        Base.Loading.hide();
        return;
      }

      Base.Messages.setMessage({
        type: "success",
        description: result.message,
      });

      this.reset();
    },
  },
  template: `
  <div>
    <div class="d-flex justify-content-start">
      <div class="box me-4">
        Project:<br />
        <strong class="fs-3">{{ projectName }}</strong>
      </div>

      <div class="box me-4">
        Project ID:<br />
        <strong class="fs-6" style="line-height: 2.8rem">
          {{ projectId }}
        </strong>
      </div>

      <div class="box flex-fill d-flex">
        <div>
          Migration Status: <br />
          <strong class="fs-5 lh-lg">{{ projectStatus }}</strong>
        </div>
      </div>
    </div>

    <div v-if="!hasMigrationData && !wasRemoved">
      <button class="btn btn-primary me-3" @click="startMigration">
        Migrate this project
      </button>
      <button class="btn btn-danger" @click="removeProject">
        Remove this project
      </button>
    </div>

    <div class="alert alert-danger" v-if="!hasMigrationData && wasRemoved">
      <p>This project has been marked for removal.</p>
      <button class="btn btn-danger" @click="undoRemoveProject">
        Undo Project Removal
      </button>
    </div>

    <div v-if="hasMigrationData" class="d-flex justify-content-between">
      <div class="box-table me-4 flex-fill">
        <table class="table">
          <thead>
            <tr><th colspan="2">Swift Data</th></tr>
          </thead>
          <tbody>
            <tr>
              <th width="25%">Containers</th>
              <td>{{ migrationData.container_count_swift }}</td>
            </tr>
            <tr>
              <th>Objects</th>
              <td>{{ migrationData.object_count_swift }}</td>
            </tr>
            <tr>
              <th>Total bytes</th>
              <td>{{ migrationData.bytes_used_swift }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="box-table flex-fill">
        <table class="table">
          <thead>
            <tr><th colspan="2">Migrated Data</th></tr>
          </thead>
          <tbody>
            <tr>
              <th width="25%">Containers</th>
              <td>{{ migrationData.container_count_gcp }}</td>
            </tr>
            <tr>
              <th>Objects</th>
              <td>{{ migrationData.object_count_gcp }}</td>
            </tr>
            <tr>
              <th>Total bytes</th>
              <td>{{ migrationData.bytes_used_gcp }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="hasMigrationData">
      <h5 class="mb-3">Migration Info</h5>
      <div class="box-table p-2">
        <code>
          started: {{ migrationData.initial_date }}<br />
          finished: {{ migrationData.final_date }}<br />
          errors: {{ migrationData.count_error }}<br />
          environment: {{ migrationData.environment }}<br />
          last object: {{ migrationData.last_object }}
        </code>
      </div>
    </div>
  </div>
  `,
};

new Vue(ProjectStatusApp);
