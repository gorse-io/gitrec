<template>
  <div id="app">
    <div>
      <nav :class="[primaryColor]">
        <div class="nav-wrapper container">
          <span style="font-weight: 300; font-size: 1.5rem">Privacy Policy</span>
        </div>
      </nav>
    </div>
    <div class="container sign-in-body">
      <p>This Privacy Policy describes how GitRec (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) collects, uses,
        and discloses information from users of our GitRec Chrome extension (&quot;Extension&quot;). By installing and
        using the Extension, you agree to the terms of this Privacy Policy.</p>
      <hr>
      <h5 id="1-information-we-collect">1. Information We Collect</h5>
      <p>GitRec is designed to recommend GitHub repositories to users based on their interactions. To achieve this, we
        collect the following information:</p>
      <ul>
        <li><strong>GitHub Data</strong>: We collect information about your interactions on GitHub, specifically your
          <strong>starred repositories</strong> and <strong>repositories you have read</strong>. This information is
          used to build your recommendation profile. We do not collect any other personal data from your GitHub account.
        </li>
      </ul>
      <hr>
      <h5 id="2-how-we-use-your-information">2. How We Use Your Information</h5>
      <p>The information we collect is used solely for the following purpose:</p>
      <ul>
        <li><strong>Repository Recommendations</strong>: We use your starred and read repository data to build a
          personalized recommendation model. This model helps us suggest new, relevant repositories to you.</li>
      </ul>
      <hr>
      <h5 id="3-data-storage-and-security">3. Data Storage and Security</h5>
      <ul>
        <li><strong>Storage</strong>: Your GitHub data is sent to and stored on our servers at the URL <strong><a
              href="http://gitrec.gorse.io/">http://gitrec.gorse.io/</a></strong>.</li>
        <li><strong>Security</strong>: We take reasonable measures to protect your information from unauthorized access,
          use, or disclosure. However, no method of transmission over the internet or electronic storage is 100% secure.
          Therefore, we cannot guarantee its absolute security.</li>
      </ul>
      <hr>
      <h5 id="4-disclosure-of-your-information">4. Disclosure of Your Information</h5>
      <p>We do not sell, trade, or otherwise transfer your personal information to outside parties. The data we collect
        is used exclusively for the functionality of the GitRec Extension. We may disclose your information if required
        by law or to protect our rights or the safety of others.</p>
      <hr>
      <h5 id="5-your-choices">5. Your Choices</h5>
      <p>If you no longer wish for your data to be collected, you can uninstall the GitRec Extension from your Chrome
        browser. Uninstalling the Extension will stop all future data collection.</p>
      <hr>
      <h5 id="6-changes-to-this-privacy-policy">6. Changes to This Privacy Policy</h5>
      <p>We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new
        Privacy Policy on this page. You are advised to review this Privacy Policy periodically for any changes.</p>
      <hr>
      <h5 id="7-contact-us">7. Contact Us</h5>
      <p>If you have any questions about this Privacy Policy, please contact us at:</p>
      <ul>
        <li><strong>Email</strong>: <strong>zhangzhenghao@hotmail.com</strong></li>
      </ul>
    </div>
  </div>
</template>

<script>
import M from "@materializecss/materialize";

export default {
  data() {
    return {
      primaryColor: "blue darken-1",
      textColor: "white-text text-lighten-3",
    };
  },
  mounted() {
    M.AutoInit();
  },
};
</script>

<style>
.sign-in-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 45px;
}
</style>
