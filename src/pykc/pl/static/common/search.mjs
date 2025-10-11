import { onPageLoad } from "../utils.mjs";

import { socketFactory, socketRef } from "../sockets.mjs";
import { baseUrl } from "../page-state.mjs";
import { subprotocols } from "../headers.mjs";
import {
  getListContainer,
  initializeResourceList,
} from "../resource-content.mjs";

/**
 * @typedef {{ type: 'SEARCH_RESULT', members: Array<{ res_id: number, member_moniker: string }>, events: Array<{ res_id: number, event_title: string }> }} SearchResultMsg
 */

const searchFactory = socketFactory(
  "/live/quicksearch",
  subprotocols(),
  (socket) => {
    const memberListName = "member_search_result";
    const eventListName = "event_search_result";
    const memberListContainer = getListContainer(memberListName);
    const eventListContainer = getListContainer(eventListName);
    const noResultsHtml = "<p>No Results Found</p><hr/>";
    socket.addEventListener("message", (ev) => {
      /** @type SearchResultMsg */
      const data = JSON.parse(ev.data);

      if (data.type === "SEARCH_RESULT") {
        if (data.members.length === 0) {
          memberListContainer.innerHTML = noResultsHtml;
        } else {
          initializeResourceList(memberListName, data.members);
        }
        if (data.events.length === 0) {
          eventListContainer.innerHTML = noResultsHtml;
        } else {
          initializeResourceList(eventListName, data.events);
        }
      }
    });
  },
);

onPageLoad(async () => {
  const [getSearchSocket, setSearchSocket, closeSearchSocket] = socketRef();
  const searchBar = document.querySelector("#search-box");
  const searchBtn = document.querySelector("#toggle-quicksearch-btn");
  const searchModal = document.querySelector("#quicksearch-modal");
  searchBtn.addEventListener("click", (_ev) => {
    setSearchSocket(searchFactory());
    searchModal.showModal();
    // if (searchModal.open) {
    //   closeSearchSocket();
    //   searchModal.close();
    // } else {
    //   setSearchSocket(searchFactory());
    //   searchModal.show();
    // }
  });

  searchBar.addEventListener("input", (_ev) => {
    getSearchSocket().send(searchBar.value);
  });

  searchModal.addEventListener("close", closeSearchSocket);

  // searchBar.addEventListener("click", (_ev) => {
  //   setSearchSocket(searchFactory());
  //   searchResultsContainer.show();
  //
  // });
  // searchBar.addEventListener("blur", (_ev) => {
  //   closeSearchSocket();
  //   searchResultsContainer.close();
  // });
});
