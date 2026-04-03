import { createApp } from "vue";
import App from "./App.vue";
import "@materializecss/materialize/dist/css/materialize.min.css";
import "github-markdown-css/github-markdown.css";
import 'material-design-icons-iconfont/dist/material-design-icons.css';
import "@fortawesome/fontawesome-free/css/all.css";

const app = createApp(App);
app.mount("#app");
