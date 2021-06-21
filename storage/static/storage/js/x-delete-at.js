
const XDeleteInput = {
  template: `
  <span>
    x-delete-at: <input type="text" value="" />
  </span>
  `
};

const XDeleteAt = {
  el: '#x-delete-at',
  components: {
    'x-delete-input': XDeleteInput
  },
  data: {

  },
  methods: {
    send() {
      // fetch(url, data);
    }
  },
  template: `
  <div class="form-box">
    <div class="content">
      <x-delete-input></x-delete-input>
    </div>
  </div>
  `
};

new Vue(XDeleteAt);
