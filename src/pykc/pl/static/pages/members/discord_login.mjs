import { onPageLoad } from "../../utils.mjs";
import {
  discordLogin,
  redirectLoginOrShowErrorMsg,
} from "../../members/login.mjs";
import { getQueryParam } from "../../page-state.mjs";

onPageLoad(async () => {
  const discordAccessCode = getQueryParam("code");
  const discordState = getQueryParam("state");
  const loginRes = await discordLogin({
    code: discordAccessCode,
    state: discordState,
  });
  await redirectLoginOrShowErrorMsg(loginRes);
});
