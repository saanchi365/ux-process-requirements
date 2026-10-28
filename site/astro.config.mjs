import { defineConfig } from "astro/config";

// the site lives at https://<owner>.github.io/<repository>/
const [owner, repo] = (process.env.GITHUB_REPOSITORY || "saanchi365/ux-process-requirements").split("/");
export default defineConfig({
  site: `https://${owner}.github.io`,
  base: `/${repo}/`,
  trailingSlash: "always",
});
