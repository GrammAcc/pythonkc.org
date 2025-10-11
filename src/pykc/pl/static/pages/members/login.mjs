import { onPageLoad } from "../../utils.mjs";
import { baseUrl, getData } from "../../page-state.mjs";

onPageLoad(() => {
  const loginBtn = document.querySelector("#login-with-discord-btn");
  const redirectUrl = encodeURIComponent(baseUrl() + "/members/login/discord");
  loginBtn.addEventListener("click", (_ev) => {
    const discordState = getData("discord-oauth-state");
    window.location.assign(
      `https://discord.com/oauth2/authorize?client_id=1424077868782059591&response_type=code&redirect_uri=${redirectUrl}&scope=identify+guilds.members.read&state=${discordState}`,
    );
  });
});
