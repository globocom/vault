// globals: ALL_USERS, ALL_TEAMS, ADD_URL, DELETE_URL, LIST_URL, TEXT

const UsersTeamsMixin = {
  data() {
    return {
      allUsers: ALL_USERS,
      allTeams: ALL_TEAMS,
      addUrl: ADD_URL,
      deleteUrl: DELETE_URL,
      listUrl: LIST_URL,
      text: TEXT,
    };
  },
  methods: {
    showMsg(msg, t = "success") {
      msg = t === "error" ? `Error: ${msg}` : msg;
      Base.Messages.setMessage({ description: msg, type: t });
    },
  },
};

const TeamCard = {
  mixins: [UsersTeamsMixin],
  props: ["team", "updateFn", "userQuery"],
  data() {
    return {
      selectedUser: "",
      newUser: false,
      csrfToken: "",
    };
  },
  created() {
    this.csrfToken = Base.Cookie.read("csrftoken");
  },
  computed: {
    filteredUsers() {
      return this.team.users.filter((u) => u.name.search(this.userQuery) >= 0);
    },
  },
  methods: {
    async addUserTeam() {
      if (this.selectedUser === "") {
        this.showMsg(this.text.selectUser, "error");
        return;
      }

      const data = await fetch(this.addUrl, {
        method: "POST",
        body: `user=${this.selectedUser}&group=${this.team.id}`,
        headers: {
          "Content-type": "application/x-www-form-urlencoded",
          "X-CSRFToken": this.csrfToken,
        },
      });

      const result = await data.json();

      if (!data.ok) {
        this.showMsg(result.msg, "error");
        return;
      }

      this.showMsg(this.text.userAdded);
      this.updateFn();
      this.resetNewUser();
    },
    async removeUserTeam(userId) {
      if (!window.confirm(this.text.removeUserWarning)) {
        return;
      }

      const data = await fetch(this.deleteUrl, {
        method: "POST",
        body: `user=${userId}&group=${this.team.id}`,
        headers: {
          "Content-type": "application/x-www-form-urlencoded",
          "X-CSRFToken": this.csrfToken,
        },
      });

      const result = await data.json();

      if (!data.ok) {
        this.showMsg(result.msg, "error");
        return;
      }

      this.showMsg(this.text.userRemoved);
      this.updateFn();
    },
    toggleNewUser() {
      this.newUser = !this.newUser;
    },
    resetNewUser() {
      this.newUser = false;
      this.selectedUser = "";
    },
  },
  template: `
  <div class="card mb-4">
    <div class="card-header">
      <strong>{{ team.name }}</strong>
    </div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item d-flex justify-content-between align-items-center"
          v-for="(user, index) in filteredUsers">
        {{ user.name }}
        <button class="btn btn-sm btn-default text-danger"
                @click="removeUserTeam(user.id)">
          <i class="fas fa-times me-1"></i> {{ text.removeUser }}
        </button>
      </li>
      <li class="list-group-item d-flex justify-content-start align-items-center">
        <button class="btn btn-sm btn-outline-primary"
                v-if="!newUser"
                @click="toggleNewUser">
          <i class="fas fa-plus me-1"></i> {{ text.addNewUser }}
        </button>
        <template v-if="newUser">
          <select class="form-select form-select-sm w-50 me-1"
                  :id="'user-select-' + team.id"
                  v-model="selectedUser">
            <option disabled value="">{{ text.selectUser }}</option>
            <option v-for="user in allUsers" :value="user.id">
              {{ user.name }}
            </option>
          </select>
          <button class="btn btn-sm btn-primary me-1"
                  @click="addUserTeam">
            {{ text.add }}
          </button>
          <button class="btn btn-sm btn-outline-secondary"
                  @click="toggleNewUser">
            {{ text.cancel }}
          </button>
        </template>
      </li>
    </ul>
  </div>
  `,
};

const UserTeamsApp = {
  el: "#user-teams-app",
  mixins: [UsersTeamsMixin],
  components: {
    "team-card": TeamCard,
  },
  data: {
    teams: [],
    userFilter: "",
    loading: false,
  },
  created() {
    this.getUsersAndTeams();
  },
  methods: {
    async getUsersAndTeams() {
      const data = await fetch(this.listUrl);
      const result = await data.json();

      if (!data.ok) {
        this.showMsg(result.msg, "error");
        return;
      }

      this.teams = result;
    },
  },
  template: `
  <div id="add-user-team" class="mb-5">
    <div class="card mb-4">
      <div class="card-body">
        <div class="form-group d-flex align-items-center">
          <input type="text" class="form-control me-1 mb-0" :placeholder="text.filterUsers"
                 v-model="userFilter" />
          <button class="btn btn-outline-secondary"
                  @click="() => this.userFilter = ''">
            {{ text.clear }}
          </button>
        </div>
      </div>
    </div>

    <h4 class="mb-3">{{ text.teams }}</h4>

    <team-card v-for="team in teams"
               :team="team"
               :updateFn="getUsersAndTeams"
               :userQuery="userFilter"
               :key="team.id">
    </team-card>
  </div>
  `,
};

new Vue(UserTeamsApp);
