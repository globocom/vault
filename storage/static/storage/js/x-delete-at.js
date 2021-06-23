const XDeleteAt = {
  el: '#x-delete-at',
  data: {
    xValue: ''
  },
  methods: {
    send() {
      console.log('sending')
      let csrfToken = this.getCookie('csrftoken');
      fetch(OPTIONAL_HEADERS_URL,
        {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            'x-delete-at': this.xValue
          })
        });
    },
    getCookie(name) {
      const nameEQ = name + '=';
      const ca = document.cookie.split(';');
      for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
          c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
          return c.substring(nameEQ.length, c.length);
        }
      }
      return null;
    },

    async fetchMetadata () {
      let response = await fetch(METADATA_URL);
      return await response.json();
    }
  },
  async created () {
    let obj = await this.fetchMetadata();
    let keys = Object.keys(obj).map(a => a.toLowerCase())
    if (keys.includes('x-delete-at')){
      this.xValue = obj['X-Delete-At'];
    }
  },
  template: `
  <div class="form-box">
    <div class="content">
      x-delete-at: <input v-model="xValue" type="text" value="" placeholder="epoch timestamp"/>
      <button @click="send">Save</button>
    </div>
  </div>
  `
};

new Vue(XDeleteAt);
