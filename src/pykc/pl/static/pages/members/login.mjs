import { onPageLoad, assert } from "../../utils.mjs";
import { buildPayload, submitBtn } from "../../editing.mjs";
import { baseUrl, getData } from "../../page-state.mjs";
import {
  passwordLogin,
  redirectLoginOrShowErrorMsg,
} from "../../members/login.mjs";

onPageLoad(() => {
  const discordLoginBtn = document.querySelector("#login-with-discord-btn");
  const redirectUrl = encodeURIComponent(baseUrl() + "/members/login/discord");
  discordLoginBtn.addEventListener("click", (_ev) => {
    const discordState = getData("discord-oauth-state");
    window.location.assign(
      `https://discord.com/oauth2/authorize?client_id=1424077868782059591&response_type=code&redirect_uri=${redirectUrl}&scope=identify+guilds.members.read&state=${discordState}`,
    );
  });

  const passwordLoginBtn = assert(submitBtn("password_login"));
  passwordLoginBtn.addEventListener("click", async (_ev) => {
    const loginRes = await passwordLogin(
      buildPayload(["member_moniker", "member_pw"]),
    );
    await redirectLoginOrShowErrorMsg(loginRes);
  });
});
