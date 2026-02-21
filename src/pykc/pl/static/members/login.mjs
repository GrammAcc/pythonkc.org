// @ts-check

import { baseUrl, csrfToken } from "../page-state.mjs";

/**
 * @param {{ code: string, state: string }} payload
 * @returns {Promise<Response>} The PUT result.
 */
export async function discordLogin(payload) {
  const loginRes = await fetch(
    `${baseUrl()}/api/v1/members/authenticate/discord`,
    {
      method: "PUT",
      headers: {
        "X-CSRF-TOKEN": csrfToken(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );
  return loginRes;
}

export async function redirectLoginOrShowErrorMsg(loginRes) {
  if (loginRes.status === 200) {
    window.location.assign(`${baseUrl()}/members/account`);
  } else if (loginRes.status === 400) {
    const msg = (await loginRes.json()).detail;
    alert(msg);
  } else {
    alert("Unknown error when logging in. Please try again later.");
  }
}

/**
 * @param {{ member_moniker: string, member_pw: string }} payload
 * @returns {Promise<Response>} The PUT result.
 */
export async function passwordLogin(payload) {
  const loginRes = await fetch(
    `${baseUrl()}/api/v1/members/authenticate/password`,
    {
      method: "PUT",
      headers: {
        "X-CSRF-TOKEN": csrfToken(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );
  return loginRes;
}
