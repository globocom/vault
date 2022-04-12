// globals: ALL_USERS, ALL_TEAMS, ADD_URL, DELETE_URL, LIST_URL, TRANSLATIONS

const state = Vue.observable({
  loggedUser: LOGGED_USER,
  allUsers: ALL_USERS,
  allTeams: ALL_TEAMS,
  addUrl: ADD_URL,
  listUrl: LIST_URL,
  deleteUrl: DELETE_URL,
  teams: [],
  currentTeam: {
    id: 0,
    name: "",
  },
  csrfToken: Base.Cookie.read("csrftoken"),
});

const UsersTeamsMixin = {
  data() {
    return {
      trans: TRANSLATIONS,
      loading: false,
    };
  },
  methods: {
    async getUsersAndTeams() {
      this.loading = true;
      const data = await fetch(state.listUrl);
      const result = await data.json();

      if (!data.ok) {
        this.showMsg(result.msg, "error");
        this.loading = false;
        return;
      }

      state.teams.length = 0;
      state.teams.push(...result);
      this.loading = false;
    },
    setCurrentTeam(team) {
      state.currentTeam.id = team.id;
      state.currentTeam.name = team.name;
    },
    clearCurrentTeam() {
      state.currentTeam.id = 0;
    },
    showMsg(msg, t = "success") {
      msg = t === "error" ? `Error: ${msg}` : msg;
      Base.Messages.setMessage({ description: msg, type: t });
    },
  },
};

const UsersModal = {
  mixins: [UsersTeamsMixin],
  data() {
    return {
      query: "",
      selectedUser: "",
      currentTeam: state.currentTeam,
    };
  },
  mounted() {
    this.$nextTick(() => this.$refs.modalSearch.focus());
  },
  computed: {
    filteredAllUsers() {
      return state.allUsers.filter((u) => u.name.search(this.query) >= 0);
    },
  },
  methods: {
    async addUserTeam() {
      if (this.selectedUser === "") {
        this.showMsg(this.trans.selectUser, "warning");
        return;
      }

      const data = await fetch(state.addUrl, {
        method: "POST",
        body: `user=${this.selectedUser}&group=${state.currentTeam.id}`,
        headers: {
          "Content-type": "application/x-www-form-urlencoded",
          "X-CSRFToken": state.csrfToken,
        },
      });

      const result = await data.json();

      if (!data.ok) {
        this.showMsg(result.msg, "error");
        return;
      }

      this.showMsg(this.trans.userAdded);
      this.getUsersAndTeams();

      state.currentTeam.id = 0;
    },
    setSelected(userId) {
      this.selectedUser = userId;
    },
    close() {
      this.clearCurrentTeam();
    },
  },
  template: `
  <div class="users-modal-overlay" tabindex="0"
       @click="close"
       @keyup.esc="close">
    <div class="users-modal" @click.stop>
      <div class="users-modal-header">
        <h5 class="mb-4">{{ trans.addNewUser }}</h5>
        <button class="btn btn-sm btn-default btn-close"
                @click="close">
        </button>
        <input type="text" class="form-control" placeholder="Search"
               ref="modalSearch"
               v-model="query" />
      </div>

      <ul class="users-modal-list">
        <li v-for="user in filteredAllUsers"
            :class="{ active: selectedUser === user.id }"
            @click="setSelected(user.id)">
          <i class="fas fa-check me-2"
             v-show="selectedUser === user.id">
          </i>{{ user.name }}
        </li>
      </ul>

      <div class="users-modal-base">
        <button class="btn btn-sm btn-primary"
                @click="addUserTeam"
                :disabled="selectedUser === ''">
          {{ trans.addTo }} {{ currentTeam.name }}
        </button>
      </div>
    </div>
  </div>
  `,
};

const TeamCard = {
  mixins: [UsersTeamsMixin],
  props: ["team", "userQuery"],
  data() {
    return {
      selectedUser: "",
      loggedUser: state.loggedUser,
    };
  },
  computed: {
    filteredUsers() {
      return this.team.users.filter((u) => u.name.search(this.userQuery) >= 0);
    },
  },
  methods: {
    async removeUserTeam(userId) {
      if (!window.confirm(this.trans.removeUserWarning)) {
        return;
      }

      const data = await fetch(state.deleteUrl, {
        method: "POST",
        body: `user=${userId}&group=${this.team.id}`,
        headers: {
          "Content-type": "application/x-www-form-urlencoded",
          "X-CSRFToken": state.csrfToken,
        },
      });

      const result = await data.json();

      if (!data.ok) {
        this.showMsg(result.msg, "error");
        return;
      }

      this.showMsg(this.trans.userRemoved);
      this.getUsersAndTeams();
    },
  },
  template: `
  <div class="card mb-4">
    <div class="card-header d-flex justify-content-between">
      <strong class="fs-5">{{ team.name }}</strong>

      <button class="btn btn-sm btn-default text-primary"
              @click="setCurrentTeam(team)">
        <i class="fas fa-plus me-1"></i> {{ trans.addNewUserTeam }}
      </button>
    </div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item d-flex justify-content-between align-items-center"
          v-for="(user, index) in filteredUsers">
        {{ user.name }}
        <button class="btn btn-sm btn-default text-danger btn-remove-user"
                :disabled="user.name === loggedUser"
                @click="removeUserTeam(user.id)">
          <span class="remove-user-text me-2">{{ trans.removeUser }}</span><i class="fas fa-times"></i>
        </button>
      </li>
    </ul>
  </div>
  `,
};

const UserTeamsApp = {
  el: "#user-teams-app",
  mixins: [UsersTeamsMixin],
  components: {
    "users-modal": UsersModal,
    "team-card": TeamCard,
  },
  data: {
    teams: state.teams,
    currentTeam: state.currentTeam,
    userFilter: "",
  },
  created() {
    this.getUsersAndTeams();
  },
  template: `
  <div id="add-user-team" class="mb-5">
    <div class="mb-4 d-flex justify-content-between align-items-center">
      <h3 class="fw-light mb-0">{{ trans.myTeams }}</h3>
      <input type="text" class="form-control w-50 me-1 mb-0"
             :placeholder="trans.filterUsers"
             v-model="userFilter" />
    </div>
    <div class="d-flex justify-content-center fs-2"
         style="opacity: .25"
         v-if="loading">
      <i class="fas fa-cog fa-pulse"></i>
    </div>
    <team-card v-for="team in teams"
               :team="team"
               :userQuery="userFilter"
               :key="team.id">
    </team-card>
    <users-modal v-if="currentTeam.id"></users-modal>
  </div>
  `,
};

new Vue(UserTeamsApp);
