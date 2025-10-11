/** Get the CSRF token from the server-rendered page.
 * @returns {string} The CSRF token unique to this page.
 */
export function csrfToken() {
  return document.querySelector('meta[name="csrf-token"]').content;
}

export function baseUrl() {
  return document.querySelector('meta[name="base-url"]').content;
}

export function resourceId() {
  return document.querySelector('meta[name="resource-id"]')?.content;
}

export function getData(dataPoint) {
  return document.querySelector(`meta[name="${dataPoint}"]`)?.content;
}

export function getQueryParam(paramName) {
  const params = new URLSearchParams(document.location.search);
  return params.get(paramName);
}
