<template>
  <div class="container">
    <Preloader v-if="feedbacks == null" />
    <div v-else>
      <div class="collection">
        <a v-for="feedback in pageFeedbacks" :key="feedback.FeedbackType + feedback.ItemId"
          :href="'https://github.com/' + feedback.ItemId" target="__blank" class="collection-item">
          <i v-if="feedback.FeedbackType == 'star'" class="material-icons feedback-icon">star</i>
          <i v-if="feedback.FeedbackType == 'like'" class="material-icons feedback-icon">favorite</i>
          {{ feedback.ItemId }}
          <div class="secondary-content">
            {{ formatTime(feedback.Timestamp) }}
          </div>
        </a>
      </div>
      <ul class="pagination">
        <li :class="{'disabled': currentPage === 1, 'waves-effect': currentPage > 1}"><a @click="currentPage--"><i
              class="material-icons">chevron_left</i></a></li>
        <li v-for="index in numPage" :key="index"
          :class="index === currentPage ? ['active','blue','darken-1'] : ['waves-effect']"><a
            @click="currentPage = index">{{ index }}</a></li>
        <li :class="{'disabled': currentPage === numPage, 'waves-effect': currentPage < numPage}"><a
            @click="currentPage++"><i class="material-icons">chevron_right</i></a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
const axios = require("axios");
import * as timeago from "timeago.js";
import Preloader from "../components/Preloader.vue";

const PAGE_SIZE = 50;

export default {
  components: {
    Preloader
  },
  data() {
    return {
      currentPage: 1,
      feedbacks: null,
    };
  },
  mounted() {
    axios.get("/api/favorites", { withCredentials: true }).then((response) => {
      this.feedbacks = response.data;
    });
  },
  methods: {
    formatTime(timestamp) {
      return timeago.format(timestamp);
    },
  },
  computed: {
    numPage: function () {
      if (this.feedbacks == null) {
        return 0;
      }
      return Math.ceil(this.feedbacks.length / PAGE_SIZE);
    },
    pageFeedbacks: function () {
      if (this.feedbacks == null) {
        return [];
      }
      return this.feedbacks.slice(PAGE_SIZE * (this.currentPage - 1), PAGE_SIZE * this.currentPage);
    }
  }
};
</script>

<style>
.feedback-icon {
  font-size: 16px;
  vertical-align: middle;
}
</style>
