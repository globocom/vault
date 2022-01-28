// global UPLOAD_PARAMS
const { uploadUrl, signature, expires, maxFileSize, maxFileCount } =
  UPLOAD_PARAMS;

const FileItem = {
  props: ["item", "upload", "queue"],
  computed: {
    disabledUpload() {
      return (
        this.item.uploading ||
        this.item.uploaded ||
        this.item.error ||
        this.queue
      );
    },
  },
  methods: {
    async uploadMe() {
      return await this.upload(this.item);
    },
  },
  template: `
  <div class="upload-file-item">
    <span :class="{ 'text-success': item.uploaded,
                    'text-danger': item.error,
                    'text-muted': item.uploading }">
      <i class="far fa-file me-2"></i> {{ item.file.name }}
    </span>
    <button class="btn btn-sm btn-light upload-btn-single"
            @click="uploadMe"
            :disabled="disabledUpload">
      <i class="fas fa-spinner fa-pulse" v-show="item.uploading"></i>
      <i class="fas fa-check text-success" v-show="item.uploaded"></i>
      <i class="fas fa-cloud-upload-alt" v-show="!item.uploading && !item.uploaded && !item.error"></i>
      <i class="fas fa-times text-danger" v-show="!item.uploading && !item.uploaded && item.error"></i>
    </button>
  </div>
  `,
};

const UploadApp = {
  el: "#upload-app",
  components: {
    "file-item": FileItem,
  },
  data: {
    uploadUrl,
    signature,
    expires,
    maxFileSize,
    maxFileCount,
    maxConcurrent: 3,
    fileItems: [],
    loading: true,
    hasUploadUrlAccess: false,
  },
  async beforeMount() {
    const url = new URL(this.uploadUrl);
    const ctrl = new AbortController();
    const timeoutId = setTimeout(() => ctrl.abort(), 15000);

    try {
      await fetch(`${url.origin}/info`, {
        method: "HEAD",
        mode: "no-cors",
        signal: ctrl.signal,
      });
      this.hasUploadUrlAccess = true;
    } catch (err) {
      this.hasUploadUrlAccess = false;
      console.log(`${err} (Request to upload url timed out)`);
    }

    clearTimeout(timeoutId);
    this.loading = false;
  },
  computed: {
    maxFiles() {
      return Number(this.maxFileCount);
    },
    queue() {
      return this.fileItems.filter((f) => f.queued).length > 0;
    },
    uploadingCount() {
      return this.fileItems.filter((f) => f.uploading).length;
    },
    finished() {
      return (
        this.fileItems.length > 0 &&
        this.fileItems.length ===
          this.fileItems.filter((f) => f.uploaded).length
      );
    },
  },
  methods: {
    uploadItem(item) {
      const fData = new FormData();
      fData.append("max_file_size", this.maxFileSize);
      fData.append("max_file_count", this.maxFileCount);
      fData.append("expires", this.expires);
      fData.append("signature", this.signature);
      fData.append("file", item.file);

      item.uploading = true;

      fetch(this.uploadUrl, {
        method: "POST",
        body: fData,
        mode: "no-cors",
      })
        .then((res) => res)
        .then((res) => {
          item.uploaded = true;
          item.uploading = false;
          item.queued = false;
          this.uploadNext();
        })
        .catch((err) => {
          console.error("Upload error: ", err);
          item.error = true;
          item.uploading = false;
        });
    },
    uploadFiles() {
      console.log("Starting upload queue...");
      for (let f of this.fileItems) {
        f.queued = !f.uploaded;
      }
      this.uploadNext();
    },
    uploadNext() {
      if (!this.queue) {
        return;
      }

      for (let i of this.fileItems) {
        if (i.queued && !i.uploaded && !i.uploading) {
          this.uploadItem(i);
        }

        if (this.uploadingCount >= this.maxConcurrent) {
          return;
        }
      }
    },
    setFiles(event) {
      this.fileItems = [];
      const selectedFiles = event.target.files;

      if (selectedFiles.length > this.maxFiles) {
        Base.Messages.setMessage({
          type: "warning",
          description: `${selectedFiles.length} files is too many!`,
        });
        this.resetFiles();
        return;
      }

      for (let i = 0, l = selectedFiles.length; i < l; i++) {
        this.fileItems.push({
          file: selectedFiles[i],
          uploading: false,
          uploaded: false,
          queued: false,
          error: false,
        });
      }
    },
    resetFiles() {
      this.fileItems = [];
      this.$refs.files.value = "";
    },
  },
  template: `
  <div>
    <div class="alert alert-danger" v-if="!loading && !hasUploadUrlAccess">
      <strong>Your browser/computer don't have access to this Upload URL:</strong> <br />
      <a :href="uploadUrl">{{ uploadUrl }}</a> <br />
      <br />
      Request access to your network administrator.
    </div>
    <div class="form-box" v-if="!loading && hasUploadUrlAccess">
      <div class="content">
        <input class="form-control" type="file" name="files" multiple ref="files"
                @change="setFiles" />
        <small class="form-text text-muted">
          Select up to {{ maxFiles }} files to upload.
        </small>
        <hr />
        <div v-if="finished" class="upload-finished mb-3">
          All files uploaded!
        </div>
        <file-item v-for="(item, i) in fileItems"
                  :item="item"
                  :upload="uploadItem"
                  :queue="queue"
                  :key="'f'+i"></file-item>
      </div>
      <div class="base d-flex justify-content-between">
        <button class="btn btn-sm btn-danger"
                @click="resetFiles"
                :disabled="!fileItems.length || queue">
          Clear
        </button>
        <button class="btn btn-sm btn-primary"
                @click="uploadFiles"
                :disabled="!fileItems.length || queue || finished">
          Upload All
        </button>
      </div>
    </div>
  </div>
  `,
};

new Vue(UploadApp);
