<template>
  <div>
    <v-alert v-if="feedbacks != null && error" type="error" variant="tonal">
      <div class="login-alert__text">
        {{ error }}
      </div>
    </v-alert>

    <v-container v-else>
      <Preloader v-if="feedbacks == null" />
      <div v-else>
        <v-list class="feedback-list" lines="one">
          <v-list-item
            v-for="feedback in pageFeedbacks"
            :key="feedback.FeedbackType + feedback.ItemId"
            :href="'https://github.com/' + feedback.ItemId"
            target="_blank"
            rounded="lg"
            class="feedback-item"
          >
            <template #prepend>
              <v-icon size="18" class="feedback-icon">{{ feedbackIcon(feedback.FeedbackType) }}</v-icon>
            </template>

            <v-list-item-title>{{ feedback.ItemId }}</v-list-item-title>

            <template #append>
              <span class="feedback-time">{{ formatTime(feedback.Timestamp) }}</span>
            </template>
          </v-list-item>
        </v-list>

        <div v-if="numPage > 1" class="d-flex justify-center my-4">
          <v-pagination v-model="currentPage" :length="numPage" :total-visible="7" color="primary" />
        </div>
      </div>
    </v-container>
  </div>
</template>

<script>
import axios from "axios";
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
      error: null,
    };
  },
  mounted() {
    this.fetchFavorites();
  },
  methods: {
    fetchFavorites() {
      this.error = null;
      this.feedbacks = null;
      axios
        .get("/api/favorites", { withCredentials: true })
        .then((response) => {
          this.feedbacks = response.data;
        })
        .catch((error) => {
          this.error = error.response?.data?.error || "Failed to fetch favorites.";
          this.feedbacks = [];
        });
    },
    formatTime(timestamp) {
      return timeago.format(timestamp);
    },
    feedbackIcon(feedbackType) {
      return feedbackType === "star" ? "mdi-star" : "mdi-heart";
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
.login-alert__text {
  white-space: normal;
  line-height: 1.5;
}

.feedback-icon {
  font-size: 16px;
  vertical-align: middle;
}

.feedback-item {
  margin-bottom: 4px;
  border: 1px solid #e5e7eb;
}

.feedback-time {
  color: #6b7280;
  font-size: 0.875rem;
}
</style>
