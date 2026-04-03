<template>
  <v-app>
    <!-- Navigation Bar -->
    <v-app-bar color="primary" density="comfortable">
      <v-container class="d-flex align-center">
        <span class="text-h5 font-weight-light">Privacy Policy</span>
      </v-container>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container class="py-8">
        <v-row justify="center">
          <v-col cols="12" md="8">
            <p>
              This Privacy Policy describes how GitRec ("we," "us," or "our") collects, uses,
              and discloses information from users of our GitRec Chrome extension ("Extension").
              By installing and using the Extension, you agree to the terms of this Privacy Policy.
            </p>

            <v-divider class="my-4"></v-divider>

            <h5 class="text-h5 mb-2">1. Information We Collect</h5>
            <p>
              GitRec is designed to recommend GitHub repositories to users based on their interactions.
              To achieve this, we collect the following information:
            </p>
            <ul class="ml-4 mb-4">
              <li>
                <strong>GitHub Data</strong>: We collect information about your interactions on GitHub,
                specifically your <strong>starred repositories</strong> and <strong>repositories you have read</strong>.
                This information is used to build your recommendation profile. We do not collect any other
                personal data from your GitHub account.
              </li>
            </ul>

            <v-divider class="my-4"></v-divider>

            <h5 class="text-h5 mb-2">2. How We Use Your Information</h5>
            <p>The information we collect is used solely for the following purpose:</p>
            <ul class="ml-4 mb-4">
              <li>
                <strong>Repository Recommendations</strong>: We use your starred and read repository data
                to build a personalized recommendation model. This model helps us suggest new, relevant
                repositories to you.
              </li>
            </ul>

            <v-divider class="my-4"></v-divider>

            <h5 class="text-h5 mb-2">3. Data Storage and Security</h5>
            <ul class="ml-4 mb-4">
              <li>
                <strong>Storage</strong>: Your GitHub data is sent to and stored on our servers at the URL
                <strong><a href="http://gitrec.gorse.io/" class="text-primary">http://gitrec.gorse.io/</a></strong>.
              </li>
              <li>
                <strong>Security</strong>: We take reasonable measures to protect your information from
                unauthorized access, use, or disclosure. However, no method of transmission over the internet
                or electronic storage is 100% secure. Therefore, we cannot guarantee its absolute security.
              </li>
            </ul>

            <v-divider class="my-4"></v-divider>

            <h5 class="text-h5 mb-2">4. Disclosure of Your Information</h5>
            <p>
              We do not sell, trade, or otherwise transfer your personal information to outside parties.
              The data we collect is used exclusively for the functionality of the GitRec Extension.
              We may disclose your information if required by law or to protect our rights or the safety of others.
            </p>

            <v-divider class="my-4"></v-divider>

            <h5 class="text-h5 mb-2">5. Your Choices</h5>
            <p>
              If you no longer wish for your data to be collected, you can uninstall the GitRec Extension
              from your Chrome browser. Uninstalling the Extension will stop all future data collection.
            </p>

            <v-divider class="my-4"></v-divider>

            <h5 class="text-h5 mb-2">6. Changes to This Privacy Policy</h5>
            <p>
              We may update our Privacy Policy from time to time. We will notify you of any changes by posting
              the new Privacy Policy on this page. You are advised to review this Privacy Policy periodically
              for any changes.
            </p>

            <v-divider class="my-4"></v-divider>

            <h5 class="text-h5 mb-2">7. Contact Us</h5>
            <p>If you have any questions about this Privacy Policy, please contact us at:</p>
            <ul class="ml-4 mb-4">
              <li><strong>Email</strong>: <strong>zhangzhenghao@hotmail.com</strong></li>
            </ul>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'Privacy'
}
</script>
