import { csrfToken } from "./page-state.mjs";

export function csrfHeaders() {
  return { "X-CSRF-TOKEN": csrfToken() };
}

export function subprotocols() {
  return ["x-none", `csrf${csrfToken()}`];
}
