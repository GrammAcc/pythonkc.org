import { onPageLoad } from "../../utils.mjs";
import { buildPayload, createSocketFactory } from "../../editing.mjs";
import {
  passwordLogin,
  redirectLoginOrShowErrorMsg,
} from "../../members/login.mjs";

onPageLoad(() => {
  const onJoinSuccess = async (_res) => {
    const loginPayload = buildPayload(["member_moniker", "member_pw"]);
    const loginRes = await passwordLogin(loginPayload);
    await redirectLoginOrShowErrorMsg(loginRes);
  };

  const joinFactory = createSocketFactory("members", "member", onJoinSuccess);
  joinFactory();

  const joinBtn = document.querySelector("#join-discord-btn");
  joinBtn.addEventListener("click", () => {
    alert("discord server invites not implemented yet");
  });
});
