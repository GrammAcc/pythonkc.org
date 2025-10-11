import { baseUrl } from "./page-state.mjs";
import { assert } from "./utils.mjs";

const itemId = (listName, resId) => {
  return `${listName}-${resId}`;
};

export const getListContainer = (listName) => {
  return assert(document.querySelector(`#${listName}-list`));
};

const getItemEl = (listName, resId) => {
  return assert(document.querySelector(`#${itemId(listName, resId)}`));
};

const getDataEl = (listName, resId) => {
  return assert(document.querySelector(`#${itemId(listName, resId)}-data`));
};

const getActionsEl = (listName, resId) => {
  return assert(document.querySelector(`#${itemId(listName, resId)}-actions`));
};

const buildBaseEl = (listName, resId) => {
  const newEl = document.createElement("article");
  const elId = itemId(listName, resId);
  newEl.id = elId;
  const dataContainer = document.createElement("span");
  dataContainer.id = `${elId}-data`;
  const actionContainer = document.createElement("span");
  actionContainer.id = `${elId}-actions`;
  const sep = document.createElement("hr");
  newEl.appendChild(dataContainer);
  newEl.appendChild(actionContainer);
  newEl.appendChild(sep);
  return [newEl, dataContainer, actionContainer];
};

const buildEl = (listName, resId, innerHtml) => {
  const [newEl, dataEl] = buildBaseEl(listName, resId);
  dataEl.innerHTML = innerHtml;
  return newEl;
};

const buildMemberItemHtml = (memberData) => {
  return `
<p><a class="inline-link" href="${baseUrl()}/members/${memberData.res_id}">@${memberData.member_moniker}</a></p>
<p>${memberData.member_role}</p>
<p>${memberData.member_first_name} ${memberData.member_last_name}</p>
<p>${memberData.member_pronouns}</p>`;
};

const buildVenueItemHtml = (venueData) => {
  return `
<p><a class="inline-link" href="${baseUrl()}/events/venue/${venueData.venue_id ?? venueData.res_id}">${venueData.venue_name}</a></p>
<p>${venueData.venue_city}, ${venueData.venue_state} ${venueData.venue_postal_code}</p>
<p>${venueData.venue_address_line1}</p>
${venueData.venue_address_line2 ? "<p>" + venueData.venue_address_line2 + "</p>" : ""}
${venueData.venue_address_line3 ? "<p>" + venueData.venue_address_line3 + "</p>" : ""}`;
};

const buildEventVenueHtml = (eventData) => {
  return `
${buildVenueItemHtml(eventData)}
<p>${eventData.event_location_details}</p>
<p><span>A/V Capable: </span>${eventData.event_is_av_capable ? "Yes" : "No"}</p>`;
};

const buildRecurringItemHtml = (recurringData) => {
  return `
<a class="inline-link" href="${baseUrl()}/events/recurring/${recurringData.recurring_id ?? recurringData.res_id}">${recurringData.recurring_title}</a>
<br/>
<p>${recurringData.recurring_description}</p>
<p><span>Interval: </span>${recurringData.recurring_interval_summary}</p>
<p><span>Next Scheduled Date: </span>${recurringData.recurring_next_scheduled_date}</p>`;
};

const buildEventItemHtml = (eventData) => {
  return `
<a class="inline-link" href="${baseUrl()}/events/event/${eventData.event_id ?? eventData.res_id}">${eventData.event_is_cancelled ? "CANCELLED" : ""} ${eventData.event_title}</a>
<br/>
<p>${eventData.event_description}</p>
<br/>
<a class="inline-link" href="${eventData.event_external_link}">External Event Page</a>
<br/>
<p><span>From: </span>${eventData.event_start}</p>
<p><span>To: </span>${eventData.event_end}</p>
<br/>
${eventData.venue_id ? buildEventVenueHtml(eventData) : "<p>No Venue Reserved</p>"}`;
};

const buildUpcomingEventItemHtml = (eventData) => {
  return buildEventItemHtml(eventData);
};

const buildPastEventItemHtml = (eventData) => {
  return buildEventItemHtml(eventData);
};

const buildMemberSearchResultHtml = (memberData) => {
  // TODO: Add search-specific html structure for members in the quicksearch results.
  return buildMemberItemHtml(memberData);
};

const buildEventSearchResultHtml = (memberData) => {
  // TODO: Add search-specific html structure for events in the quicksearch results.
  return buildUpcomingEventItemHtml(memberData);
};

export const buildResourceHtml = {
  member: buildMemberItemHtml,
  upcoming_event: buildUpcomingEventItemHtml,
  past_event: buildPastEventItemHtml,
  venue: buildVenueItemHtml,
  recurring: buildRecurringItemHtml,
  member_search_result: buildMemberSearchResultHtml,
  event_search_result: buildEventSearchResultHtml,
};

/**
 * @param {string} listName
 * @param {number} resId
 * @param {object} resource
 * @returns {void}
 */
export const updateListItem = (listName, resource) => {
  const updateTarget = getDataEl(listName, resource.res_id);
  const newItemHtml = buildResourceHtml[listName](resource);
  updateTarget.innerHTML = newItemHtml;
};

/**
 * @param {string} listName
 * @param {object} resource
 * @returns {void}
 */
export const addListItem = (listName, resource) => {
  const container = getListContainer(listName);
  const listItemHtml = buildResourceHtml[listName](resource);
  const listItem = buildEl(listName, resource.res_id, listItemHtml);
  container.prepend(listItem);
};

/**
 * @param {string} listName
 * @param {number} resId
 * @returns {void}
 */
export const removeListItem = (listName, resId) => {
  getItemEl(listName, resId).remove();
};

/**
 * @param {string} listName
 * @param {number} resId
 * @param {HTMLButtonElement} btnEl
 * @returns {void}
 */
export const addListAction = (listName, resId, btnEl) => {
  const updateTarget = getActionsEl(listName, resId);
  updateTarget.appendChild(btnEl);
};

/**
 * @param {string} listName
 * @param {object[]} resources
 * @returns {Promise<void>}
 */
export const initializeResourceList = (listName, resources) => {
  const container = getListContainer(listName);
  container.innerHTML = "";

  for (const resource of resources) {
    addListItem(listName, resource);
  }
};
