import { assert, onPageLoad } from "../../utils.mjs";
import { buildPayload, submitBtn } from "../../editing.mjs";
import {
  loginMember,
  redirectLoginOrShowErrorMsg,
} from "../../members/login.mjs";
import { getData, getQueryParam } from "../../page-state.mjs";

onPageLoad(async () => {
  const discordAccessCode = getQueryParam("code");
  const discordState = getQueryParam("state");
  const loginRes = await loginMember({
    code: discordAccessCode,
    state: discordState,
  });
  await redirectLoginOrShowErrorMsg(loginRes);
});
