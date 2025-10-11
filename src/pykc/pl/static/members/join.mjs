// @ts-check

import { baseUrl, csrfToken } from "../page-state.mjs";

/**
 * @param {{ first_name: string, last_name: string, moniker: string, pw: string }} payload
 * @returns {Promise<Response>} The POST result.
 */
export async function joinMember(payload) {
  const joinRes = await fetch(`${baseUrl()}/api/v1/members/member/create`, {
    method: "POST",
    headers: {
      "X-CSRF-TOKEN": csrfToken(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return joinRes;
}
