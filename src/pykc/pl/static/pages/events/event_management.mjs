import {
  createSocketFactory,
  editSocketFactory,
  listSocketFactory,
} from "../../editing.mjs";
import { makeConfirmModal, makeModal, makeModalBtn } from "../../modals.mjs";
import { baseUrl, csrfToken } from "../../page-state.mjs";
import { addListAction, getListContainer } from "../../resource-content.mjs";
import { onPageLoad } from "../../utils.mjs";
import { socketRef } from "../../sockets.mjs";

const makeActionBtn = (elId, displayText) => {
  const newBtn = document.createElement("button");
  newBtn.id = elId;
  newBtn.classList.add("action-btn");
  newBtn.textContent = displayText;
  return newBtn;
};

onPageLoad(async () => {
  const eventListName = "upcoming_event";
  const eventResName = "event";
  const venueListName = "venue";
  const venueResName = "venue";
  const appName = "events";
  const recurringResName = "recurring";
  const recurringListName = "recurring";

  const [getInputsSocket, setInputsSocket, closeInputsSocket] = socketRef();
  const [getEventListSocket, setEventListSocket, closeEventListSocket] =
    socketRef();
  const [
    getRecurringListSocket,
    setRecurringListSocket,
    closeRecurringListSocket,
  ] = socketRef();
  const [getVenueListSocket, setVenueListSocket, closeVenueListSocket] =
    socketRef();

  const eventModal = makeModal(eventResName);
  const recurringModal = makeModal(recurringResName);
  const venueModal = makeModal(venueResName);

  const cancelEventHandler = (resId) => {
    return async (_ev) => {
      const putUrl = `${baseUrl()}/api/v1/events/event/${resId}/cancel`;
      const res = await fetch(putUrl, {
        method: "PATCH",
        headers: { "X-CSRF-TOKEN": csrfToken(), "Content-Type": "text/plain" },
      });

      if (res.status !== 200) {
        alert("cancel event failed with unknown error. Try again later.");
      }
    };
  };

  const deleteRecurringHandler = (resId) => {
    return async (_ev) => {
      const postUrl = `${baseUrl()}/api/v1/events/recurring/${resId}/delete`;
      const res = await fetch(postUrl, {
        method: "DELETE",
        headers: { "X-CSRF-TOKEN": csrfToken(), "Content-Type": "text/plain" },
      });

      if (res.status !== 200) {
        alert("delete recurring failed with unknown error. Try again later.");
      }
    };
  };

  const deleteVenueHandler = (resId) => {
    return async (_ev) => {
      const putUrl = `${baseUrl()}/api/v1/events/venue/${resId}/delete`;
      const res = await fetch(putUrl, {
        method: "DELETE",
        headers: { "X-CSRF-TOKEN": csrfToken(), "Content-Type": "text/plain" },
      });

      if (res.status !== 200) {
        alert("delete venue failed with unknown error. Try again later.");
      }
    };
  };

  const scheduleNextHandler = (resId) => {
    return async (_ev) => {
      const postUrl = `${baseUrl()}/api/v1/events/recurring/${resId}/schedule-next`;
      const res = await fetch(postUrl, {
        method: "POST",
        headers: { "X-CSRF-TOKEN": csrfToken(), "Content-Type": "text/plain" },
      });

      if (res.status !== 201) {
        alert(
          "Scheduling next event in series failed with unknown error. Try again later.",
        );
      }
    };
  };

  const eventListFactory = listSocketFactory(appName, eventListName, (msg) => {
    const data = JSON.parse(msg.data);
    if (data.type === "INIT_LIST") {
      for (const resource of data.resources) {
        const eventId = resource.res_id;
        const editBtn = makeModalBtn(eventModal, "Edit Event");
        const editFactory = editSocketFactory(appName, eventResName, eventId);
        editBtn.addEventListener("click", (_ev) =>
          setInputsSocket(editFactory()),
        );
        addListAction(eventListName, eventId, editBtn);
        const cancelBtn = makeActionBtn(
          `cancel-${eventResName}-${eventId}-btn`,
          "Cancel Event",
        );
        const confirmCancelModal = makeConfirmModal(
          "Event will be cancelled. Continue?",
          cancelEventHandler(eventId),
        );
        cancelBtn.addEventListener("click", (_ev) =>
          confirmCancelModal.showModal(),
        );
        addListAction(eventListName, eventId, cancelBtn);
      }
    } else if (data.type === "LIST_ADD") {
      const eventId = data.resource.res_id;
      const editBtn = makeModalBtn(eventModal, "Edit Event");
      const editFactory = editSocketFactory(appName, eventResName, eventId);
      editBtn.addEventListener("click", (_ev) =>
        setInputsSocket(editFactory()),
      );
      addListAction(eventListName, eventId, editBtn);
      const cancelBtn = makeActionBtn(
        `cancel-${eventResName}-${eventId}-btn`,
        "Cancel Event",
      );
      const confirmCancelModal = makeConfirmModal(
        "Event will be cancelled. Continue?",
        cancelEventHandler(eventId),
      );
      cancelBtn.addEventListener("click", (_ev) =>
        confirmCancelModal.showModal(),
      );
      addListAction(eventListName, eventId, cancelBtn);
    }
  });

  const recurringListFactory = listSocketFactory(
    appName,
    recurringListName,
    (msg) => {
      const data = JSON.parse(msg.data);
      if (data.type === "INIT_LIST") {
        for (const resource of data.resources) {
          const recurringId = resource.res_id;
          const scheduleNextBtn = makeActionBtn(
            `schedule-next-${recurringResName}-${recurringId}-btn`,
            "Schedule Next Event",
          );
          const scheduleNextModal = makeConfirmModal(
            "A new event will be created. Continue?",
            scheduleNextHandler(recurringId),
          );
          scheduleNextBtn.addEventListener("click", (_ev) =>
            scheduleNextModal.showModal(),
          );
          addListAction(recurringListName, recurringId, scheduleNextBtn);
          const editBtn = makeModalBtn(recurringModal, "Edit Recurring Event");
          const editFactory = editSocketFactory(
            appName,
            recurringResName,
            recurringId,
          );
          editBtn.addEventListener("click", (_ev) =>
            setInputsSocket(editFactory()),
          );
          addListAction(recurringListName, recurringId, editBtn);
          const cancelBtn = makeActionBtn(
            `cancel-${recurringResName}-${recurringId}-btn`,
            "Delete Recurring Event",
          );
          const confirmCancelModal = makeConfirmModal(
            "Event series will be cancelled. Continue?",
            deleteRecurringHandler(recurringId),
          );
          cancelBtn.addEventListener("click", (_ev) =>
            confirmCancelModal.showModal(),
          );
          addListAction(recurringListName, recurringId, cancelBtn);
        }
      } else if (data.type === "LIST_ADD") {
        const recurringId = data.resource.res_id;
        const scheduleNextBtn = makeActionBtn(
          `schedule-next-${recurringResName}-${recurringId}-btn`,
          "Schedule Next Event",
        );
        const scheduleNextModal = makeConfirmModal(
          "A new event will be created. Continue?",
          scheduleNextHandler(recurringId),
        );
        scheduleNextBtn.addEventListener("click", (_ev) =>
          scheduleNextModal.showModal(),
        );
        addListAction(recurringListName, recurringId, scheduleNextBtn);
        const editBtn = makeModalBtn(recurringModal, "Edit Recurring Event");
        const editFactory = editSocketFactory(
          appName,
          recurringResName,
          recurringId,
        );
        editBtn.addEventListener("click", (_ev) =>
          setInputsSocket(editFactory()),
        );
        addListAction(recurringListName, recurringId, editBtn);
        const cancelBtn = makeActionBtn(
          `cancel-${recurringResName}-${recurringId}-btn`,
          "Delete Recurring Event",
        );
        const confirmCancelModal = makeConfirmModal(
          "Event series will be cancelled. Continue?",
          deleteRecurringHandler(recurringId),
        );
        cancelBtn.addEventListener("click", (_ev) =>
          confirmCancelModal.showModal(),
        );
        addListAction(recurringListName, recurringId, cancelBtn);
      }
    },
  );

  const venueListFactory = listSocketFactory(appName, venueListName, (msg) => {
    const data = JSON.parse(msg.data);
    if (data.type === "INIT_LIST") {
      for (const { res_id: resId } of data.resources) {
        const editBtn = makeModalBtn(venueModal, "Edit Venue");
        const editFactory = editSocketFactory(appName, venueResName, resId);
        editBtn.addEventListener("click", (_ev) =>
          setInputsSocket(editFactory()),
        );
        addListAction(venueListName, resId, editBtn);
        const deleteBtn = makeActionBtn(
          `delete-${venueResName}-${resId}-btn`,
          "Delete Venue",
        );
        const confirmDeleteModal = makeConfirmModal(
          "Venue will be permanently deleted. Continue?",
          deleteVenueHandler(resId),
        );
        deleteBtn.addEventListener("click", (_ev) =>
          confirmDeleteModal.showModal(),
        );
        addListAction(venueListName, resId, deleteBtn);
      }
    } else if (data.type === "LIST_ADD") {
      const resId = data.resource.res_id;
      const editBtn = makeModalBtn(venueModal, "Edit Venue");
      const editFactory = editSocketFactory(appName, venueResName, resId);
      editBtn.addEventListener("click", (_ev) =>
        setInputsSocket(editFactory()),
      );
      addListAction(venueListName, resId, editBtn);
      const deleteBtn = makeActionBtn(
        `delete-${venueResName}-${resId}-btn`,
        "Delete Venue",
      );
      const confirmDeleteModal = makeConfirmModal(
        "Venue will be permanently deleted. Continue?",
        deleteVenueHandler(resId),
      );
      deleteBtn.addEventListener("click", (_ev) =>
        confirmDeleteModal.showModal(),
      );
      addListAction(venueListName, resId, deleteBtn);
    }
  });

  const createEventFactory = createSocketFactory(
    appName,
    eventResName,
    (_res) => eventModal.close(),
  );
  const createRecurringFactory = createSocketFactory(
    appName,
    recurringResName,
    (_res) => recurringModal.close(),
  );
  const createVenueFactory = createSocketFactory(
    appName,
    venueResName,
    (_res) => venueModal.close(),
  );

  const onModalClose = (_ev) => closeInputsSocket();

  eventModal.addEventListener("close", onModalClose);
  recurringModal.addEventListener("close", onModalClose);
  venueModal.addEventListener("close", onModalClose);

  const createEventBtn = makeModalBtn(eventModal, "Create New Event");
  const createRecurringBtn = makeModalBtn(
    recurringModal,
    "Create New Recurring Event",
  );
  const createVenueBtn = makeModalBtn(venueModal, "Create New Venue");

  createEventBtn.addEventListener("click", () =>
    setInputsSocket(createEventFactory()),
  );
  createRecurringBtn.addEventListener("click", () =>
    setInputsSocket(createRecurringFactory()),
  );
  createVenueBtn.addEventListener("click", () =>
    setInputsSocket(createVenueFactory()),
  );

  const eventTab = document.querySelector("#event-tab");
  const venueTab = document.querySelector("#venue-tab");

  const eventContainer = getListContainer(eventListName);
  const recurringContainer = getListContainer(recurringListName);
  const venueContainer = getListContainer(venueListName);

  eventContainer.insertAdjacentElement("beforebegin", createEventBtn);
  recurringContainer.insertAdjacentElement("beforebegin", createRecurringBtn);
  venueContainer.insertAdjacentElement("beforebegin", createVenueBtn);

  const eventTabBtn = document.querySelector("#event-tab-btn");
  const venueTabBtn = document.querySelector("#venue-tab-btn");

  eventTabBtn.addEventListener("click", () => {
    venueTab.classList.add("hidden");
    eventTab.classList.remove("hidden");
    closeVenueListSocket();
    setEventListSocket(eventListFactory());
    setRecurringListSocket(recurringListFactory());
  });

  venueTabBtn.addEventListener("click", () => {
    eventTab.classList.add("hidden");
    venueTab.classList.remove("hidden");
    closeEventListSocket();
    closeRecurringListSocket();
    setVenueListSocket(venueListFactory());
  });
});
