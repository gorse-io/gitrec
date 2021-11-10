<template>
  <div class="container">
    <div class="collection">
      <a
        v-for="feedback in feedbacks"
        :key="feedback.ItemId"
        :href="'https://github.com/' + feedback.ItemId"
        target="__blank"
        class="collection-item"
      >
        <i
          v-if="feedback.FeedbackType == 'star'"
          class="material-icons feedback-icon"
          >star</i
        >
        <i
          v-if="feedback.FeedbackType == 'like'"
          class="material-icons feedback-icon"
          >favorite</i
        >
        {{ feedback.ItemId }}
        <div class="secondary-content">
          {{ formatTime(feedback.Timestamp) }}
        </div>
      </a>
    </div>
  </div>
</template>

<script>
const axios = require("axios");
import * as timeago from "timeago.js";

export default {
  data() {
    return {
      feedbacks: [],
    };
  },
  mounted() {
    this.$emit("setTitle", "Favorites");
    axios.get("/api/favorites", { withCredentials: true }).then((response) => {
      this.feedbacks = response.data;
    });
  },
  methods: {
    formatTime(timestamp) {
      return timeago.format(timestamp);
    },
  },
};
</script>

<style>
.feedback-icon {
  font-size: 14px;
}
</style>
