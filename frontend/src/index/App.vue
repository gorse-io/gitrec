<template>
  <div id="app">
    <div>
      <nav :class="[primaryColor, 'nav-extended']">
        <div class="nav-wrapper container">
          <a href="#" data-target="mobile-demo" class="sidenav-trigger"><i class="material-icons">menu</i></a>
          <span style="font-weight: 300; font-size: 1.2rem">{{ $route.name }}</span>
          <ul id="nav-mobile" class="right hide-on-med-and-down">
            <li :class="{ 'active': $route.path == '/' || $route.path.startsWith('/topic/') }"><router-link
                to="/">Explore</router-link></li>
            <li :class="{ 'active': $route.path == '/favorites' }"><router-link to="/favorites">Favorites</router-link>
            </li>
            <li><a class="dropdown-trigger" href="https://gorse.io" data-target="dropdown1">Extensions<i
                  class="material-icons right">arrow_drop_down</i></a></li>
          </ul>
        </div>
        <div v-if="$route.path == '/' || $route.path.startsWith('/topic/')" class="nav-content container">
          <ul class="tabs tabs-transparent hide-scrollbar">
            <li v-for="topic in topics" v-bind:key="topic" class="tab">
              <router-link :to="topic == 'all' ? '/' : '/topic/' + topic">{{ topic.replace('-', ' ') }}</router-link>
            </li>
          </ul>
        </div>
      </nav>
    </div>
    <ul class="sidenav" id="mobile-demo">
      <li :class="{ 'active': $route.path == '/' || $route.path.startsWith('/topic/') }"><router-link
          to="/">Explore</router-link></li>
      <li :class="{ 'active': $route.path == '/favorites' }"><router-link to="/favorites">Favorites</router-link></li>
    </ul>
    <ul id="dropdown1" class="dropdown-content">
      <li><a href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl"
          target="_blank">Chrome Extension</a></li>
      <li><a href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa"
          target="_blank">Edge Add-on</a></li>
      <li><a href="https://addons.mozilla.org/addon/gitrec/"
          target="_blank">Firefox Add-on</a></li>
      <li><a href="https://greasyfork.org/zh-CN/scripts/453527-gitrec" target="_blank">Tampermonkey Userscript</a></li>
    </ul>
    <router-view></router-view>
  </div>
</template>

<script>
import M from "@materializecss/materialize";
export default {
  data() {
    return {
      title: null,
      primaryColor: "blue darken-1",
      textColor: "white-text text-lighten-3",
      showTopics: false,
      topics: [
        "all",
        // genres
        "book",
        "game",
        "machine-learning",
        // programming languages
        "python",
        "java",
        "cpp",
        "go",
        "javascript",
        "typescript",
        "c",
        "rust",
      ]
    };
  },
  mounted() {
    document.addEventListener("DOMContentLoaded", function () {
      var sidenavElements = document.querySelectorAll(".sidenav");
      M.Sidenav.init(sidenavElements);
      var tabsElements = document.querySelectorAll(".tabs");
      M.Tabs.init(tabsElements, {});
      var dropdownElements = document.querySelectorAll('.dropdown-trigger');
      M.Dropdown.init(dropdownElements, { constrainWidth: false });
    });
  }
};
</script>

<style>
.hide-scrollbar::-webkit-scrollbar {
  /* Chrome/Safari/Webkit */
  background: transparent;
  width: 0px;
  height: 0px;
}

.hide-scrollbar {
  /* Firefox */
  scrollbar-width: none;
  /* IE 10+ */
  -ms-overflow-style: none;
}
</style>
