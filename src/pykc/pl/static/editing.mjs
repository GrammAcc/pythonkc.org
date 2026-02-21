// @ts-check
import { subprotocols } from "./headers.mjs";
import { socketFactory } from "./sockets.mjs";
import { baseUrl, csrfToken } from "./page-state.mjs";
import { assert } from "./utils.mjs";
import {
  addListItem,
  initializeResourceList,
  removeListItem,
  updateListItem,
} from "./resource-content.mjs";

/**
 * @typedef {{ type: 'INIT_VALIDATION', fields: string[] }} ValidationInitMsg
 * @typedef {{ type: 'RESULT', success: boolean }} ValidationResultMsg
 * @typedef {{ type: 'VALIDATION', success_messages: Array<[string, string]>, failure_messages: Array<[string, string]> }} ValidationFeedbackMsg
 * @typedef {ValidationInitMsg | ValidationResultMsg | ValidationFeedbackMsg} ValidationMsg
 *
 * @typedef {{ type: 'CHANGESET', saved: Array<[string, string]>, changed: string[], unchanged: string[] }} ChangesetMsg
 *
 * @typedef {{ type: 'INIT_LIST', resources: object[] }} ListInitMsg
 * @typedef {{ type: 'LIST_UPDATE', res_id: number, resource: object }} ListUpdateMsg
 * @typedef {{ type: 'LIST_ADD', res_id: number, resource: object }} ListAddMsg
 * @typedef {{ type: 'LIST_REMOVE', res_id: number }} ListRemoveMsg
 * @typedef {ListInitMsg | ListUpdateMsg | ListAddMsg | ListRemoveMsg} ListMsg
 *
 * @typedef {{ type: 'LOOPBACK', resource: object }} LoopbackMsg
 *
 * @typedef {ValidationMsg | ChangesetMsg | ListMsg | LoopbackMsg} SocketMsg
 */

/**
 * @param {string} dataGroup
 * @returns {HTMLButtonElement | null}
 */
export function submitBtn(dataGroup) {
  return document.querySelector(`#${dataGroup}-submit-btn`);
}

/**
 * @param {string} dataGroup
 * @returns {HTMLButtonElement | null}
 */
export function cancelBtn(dataGroup) {
  return document.querySelector(`#${dataGroup}-cancel-btn`);
}

/**
 * @param {string} dataGroup
 * @returns {HTMLButtonElement | null}
 */
export function editBtn(dataGroup) {
  return document.querySelector(`#${dataGroup}-edit-btn`);
}

/**
 * @param {string} dataPoint
 * @returns {HTMLInputElement | null}
 */
export function inputField(dataPoint) {
  return document.querySelector(`#${dataPoint}-input`);
}

/**
 * @param {string} dataPoint
 * @returns {HTMLParagraphElement | null}
 */
export function infoField(dataPoint) {
  return document.querySelector(`#${dataPoint}-info`);
}

/**
 * @param {string} dataPoint
 * @returns {HTMLParagraphElement | null}
 */
export function statusField(dataPoint) {
  return document.querySelector(`#${dataPoint}-status`);
}

/**
 * @param {string} dataPoint
 * @returns {HTMLParagraphElement | null}
 */
export function validationMsgField(dataPoint) {
  return document.querySelector(`#${dataPoint}-validation-msg`);
}

/**
 * @param {string} dataPoint
 * @returns {any | undefined}
 */
function fieldValue(dataPoint) {
  const el = inputField(dataPoint);
  if (el?.getAttribute("type") === "checkbox") {
    return el.checked;
  } else {
    return el?.value ?? "";
  }
}

/**
 * @param {string[]} fieldIds
 * @returns {{ [key: string]: string }}
 */
export function buildPayload(fieldIds) {
  const payload = fieldIds.reduce((acc, idStr) => {
    const [key, val] = [idStr, idStr];
    acc[key] = fieldValue(val);
    return acc;
  }, {});
  return payload;
}

/**
 * @param {string} app
 * @param {string} resName
 * @param {string} resId
 * @param {null | ((arg0: Response) => Promise<void>)} onSuccess
 * @param {null | ((arg0: Response) => Promise<void>)} onFailure
 * @returns {() => WebSocket}
 */
export function editSocketFactory(
  app,
  resName,
  resId,
  onSuccess = null,
  onFailure = null,
) {
  const url = resId
    ? `/${app}/live/${resName}/${resId}/edit`
    : `/${app}/live/${resName}/edit`;

  const defaultSuccessHandler = async (res) => undefined;
  const defaultFailureHandler = async (res) =>
    alert(`update ${resName} failed with unknown error. Try again later`);

  const successHandler = onSuccess ?? defaultSuccessHandler;
  const failureHandler = onFailure ?? defaultFailureHandler;

  const setupSaveBtn = (dataPoints) => {
    const saveBtn = assert(submitBtn(resName));
    const newSaveBtn = saveBtn.cloneNode(true);
    saveBtn.replaceWith(newSaveBtn);
    newSaveBtn.addEventListener("click", async (_ev) => {
      const patchUrl = resId
        ? `${baseUrl()}/api/v1/${app}/${resName}/${resId}/update`
        : `${baseUrl()}/api/v1/${app}/${resName}/update`;
      const res = await fetch(patchUrl, {
        method: "PATCH",
        body: JSON.stringify(buildPayload(dataPoints)),
        headers: {
          "X-CSRF-TOKEN": csrfToken(),
          "Content-Type": "application/json",
        },
      });

      if (res.status === 200) {
        await successHandler(res);
      } else {
        await failureHandler(res);
      }
    });
  };

  return socketFactory(url, subprotocols(), (socket) => {
    setupValidationListeners(socket);

    // Note: This mapping gets mutated.
    const statusElements = {};
    // Note: This mapping gets mutated.
    const infoElements = {};
    // Note: This mapping gets mutated.
    const inputElements = {};
    // Note: This mapping gets mutated.
    const payload = {};
    // Note: This mapping gets mutated.
    const savedValues = {};

    const setupInputs = (dataPoints) => {
      for (const [dataPoint, val] of Object.entries(dataPoints)) {
        const infoEl = infoField(dataPoint);
        if (infoEl !== null) {
          infoEl.textContent = val.toString();
          infoElements[dataPoint] = infoEl;
        } else {
          const inputEl = inputField(dataPoint);
          const statusEl = statusField(dataPoint);
          if (!inputEl) {
            console.debug(`Missing primary element for ${dataPoint}`);
            continue;
          }
          if (!statusEl) {
            console.debug(`Missing status element for ${dataPoint}`);
            continue;
          }

          const isCheckbox = inputEl?.getAttribute("type") === "checkbox";

          if (inputEl !== null) {
            if (isCheckbox) {
              inputEl.checked = val;
              // @ts-ignore
              inputEl.value = inputEl.checked;
              inputEl.addEventListener("change", (_ev) => {
                payload[dataPoint] = inputEl.checked;
                socket.send(JSON.stringify(payload));
              });
            } else {
              inputEl.value = val;
              inputEl.addEventListener("input", (_ev) => {
                payload[dataPoint] = inputEl.value;
                socket.send(JSON.stringify(payload));
              });
            }
            inputElements[dataPoint] = inputEl;
            payload[dataPoint] = inputEl.value;
            savedValues[dataPoint] = inputEl.value;
          }
          // Clear any stale changeset messages.
          statusEl.textContent = "";
          statusElements[dataPoint] = statusEl;
        }
      }

      // Trigger validation on initial values.
      socket.send(JSON.stringify(payload));
    };

    socket.addEventListener("message", (ev) => {
      /** @type ValidationMsg | ChangesetMsg | LoopbackMsg */
      const data = JSON.parse(ev.data);

      if (data.type === "INIT_VALIDATION") {
        setupSaveBtn(Object.keys(data.fields));
        setupInputs(data.fields);
      } else if (data.type === "RESULT") {
        const saveBtn = assert(submitBtn(resName));
        if (data.success) {
          saveBtn.removeAttribute("disabled");
        } else {
          saveBtn.setAttribute("disabled", "true");
        }
      } else if (data.type === "CHANGESET") {
        const filteredSaved = data.saved.filter(([dataPoint, _]) => {
          return Object.keys(inputElements).includes(dataPoint);
        });
        const filteredChanged = data.changed.filter((dataPoint) => {
          return Object.keys(inputElements).includes(dataPoint);
        });
        const filteredUnchanged = data.unchanged.filter((dataPoint) => {
          return Object.keys(inputElements).includes(dataPoint);
        });

        for (const [dataPoint, savedValue] of filteredSaved) {
          const inputEl = inputElements[dataPoint];
          const el = statusElements[dataPoint];
          const val =
            inputEl.getAttribute("type") === "checkbox"
              ? inputEl.checked
              : inputEl.value;
          if (val === savedValue) {
            el.style.color = "green";
            el.textContent = "Saved!";
          } else {
            el.style.color = "orange";
            el.textContent = "Unsaved Changes";
          }
        }

        for (const dataPoint of filteredUnchanged) {
          const el = statusElements[dataPoint];
          el.style.color = "yellow";
          el.textContent = "No Changes";
        }

        for (const dataPoint of filteredChanged) {
          const el = statusElements[dataPoint];
          el.style.color = "orange";
          el.textContent = "Unsaved Changes";
        }
      } else if (data.type === "LOOPBACK") {
        for (const [dataPoint, infoEl] of Object.entries(infoElements)) {
          infoEl.textContent = data.resource[dataPoint] ?? "";
        }
      }
    });
  });
}

/**
 * @param {string} app
 * @param {string} resName
 * @param {null | ((arg0: Response) => Promise<void>)} onSuccess
 * @param {null | ((arg0: Response) => Promise<void>)} onFailure
 * @returns {() => WebSocket}
 */
export function createSocketFactory(
  app,
  resName,
  onSuccess = null,
  onFailure = null,
) {
  const url = `/${app}/live/${resName}/create`;

  return socketFactory(url, subprotocols(), (socket) => {
    setupValidationListeners(socket);

    const defaultSuccessHandler = async (res) => undefined;
    const defaultFailureHandler = async (res) => {
      alert(`create ${resName} failed with unknown error. Try again later.`);
    };

    const successHandler = onSuccess ?? defaultSuccessHandler;
    const failureHandler = onFailure ?? defaultFailureHandler;

    const setupSaveBtn = (dataPoints) => {
      const saveBtn = assert(submitBtn(resName));
      const newSaveBtn = saveBtn.cloneNode(true);
      saveBtn.replaceWith(newSaveBtn);
      newSaveBtn.addEventListener("click", async (_ev) => {
        const postUrl = `${baseUrl()}/api/v1/${app}/${resName}/create`;
        const res = await fetch(postUrl, {
          method: "POST",
          body: JSON.stringify(buildPayload(dataPoints)),
          headers: {
            "X-CSRF-TOKEN": csrfToken(),
            "Content-Type": "application/json",
          },
        });

        if (res.status === 201) {
          await successHandler(res);
        } else {
          await failureHandler(res);
        }
      });
    };

    // Note: This mapping gets mutated.
    const statusElements = {};
    // Note: This mapping gets mutated.
    const infoElements = {};

    const setupInputs = (dataPoints) => {
      // Note: This mapping gets mutated.
      const payload = {};

      for (const [dataPoint, val] of Object.entries(dataPoints)) {
        const infoEl = infoField(dataPoint);
        if (infoEl !== null) {
          infoEl.textContent = val;
          infoElements[dataPoint] = infoEl;
        } else {
          const inputEl = inputField(dataPoint);
          const statusEl = statusField(dataPoint);
          if (!inputEl) {
            console.debug(`Missing input element for ${dataPoint}`);
            continue;
          }
          if (!statusEl) {
            console.debug(`Missing status element for ${dataPoint}`);
            continue;
          }

          const isCheckbox = inputEl?.getAttribute("type") === "checkbox";

          if (inputEl !== null) {
            if (isCheckbox) {
              inputEl.checked = false;
              // @ts-ignore
              inputEl.value = inputEl.checked;
              inputEl.addEventListener("change", (_ev) => {
                payload[dataPoint] = inputEl.checked;
                socket.send(JSON.stringify(payload));
              });
            } else {
              inputEl.value = val;
              inputEl.addEventListener("input", (_ev) => {
                payload[dataPoint] = inputEl.value;
                socket.send(JSON.stringify(payload));
              });
            }
            payload[dataPoint] = inputEl.value;
          }

          // Clear any stale changeset messages.
          statusEl.textContent = "";
          statusElements[dataPoint] = statusEl;
        }
      }

      // Trigger validation on initial values.
      socket.send(JSON.stringify(payload));
    };

    // Field validation.
    socket.addEventListener("message", (ev) => {
      /** @type ValidationMsg | LoopbackMsg | ListMsg */
      const data = JSON.parse(ev.data);

      if (data.type === "INIT_VALIDATION") {
        setupSaveBtn(Object.keys(data.fields));
        setupInputs(data.fields);
      } else if (data.type === "RESULT") {
        const saveBtn = assert(submitBtn(resName));
        if (data.success) {
          saveBtn.removeAttribute("disabled");
        } else {
          saveBtn.setAttribute("disabled", "true");
        }
      } else if (data.type === "LOOPBACK") {
        for (const [dataPoint, infoEl] of Object.entries(infoElements)) {
          infoEl.textContent = data.resource[dataPoint] ?? "";
        }
      } else if (data.type === "LIST_ADD") {
        const createdStatus = Object.entries(data.resource).filter(
          ([dataPoint, _]) => {
            return Object.keys(statusElements).includes(dataPoint);
          },
        );

        for (const [dataPoint, _createdValue] of createdStatus) {
          const el = statusElements[dataPoint];
          el.style.color = "green";
          el.textContent = "Created!";
        }

        const createdInfo = Object.entries(data.resource).filter(
          ([dataPoint, _]) => {
            return Object.keys(infoElements).includes(dataPoint);
          },
        );

        for (const [dataPoint, createdValue] of createdInfo) {
          const el = infoElements[dataPoint];
          el.textContent = createdValue;
        }
      }
    });
  });
}

/**
 * @param {string} appName
 * @param {string} listName
 * @returns {() => WebSocket}
 */
export function listSocketFactory(appName, listName, additionalMessageHandler) {
  const url = `/${appName}/live/${listName}/list`;

  return socketFactory(url, subprotocols(), (socket) => {
    /** @type {{ resourceIds: number[] }} */
    const state = { resourceIds: [] };

    socket.addEventListener("message", (ev) => {
      /** @type ListMsg */
      const data = JSON.parse(ev.data);

      if (data.type === "INIT_LIST") {
        initializeResourceList(listName, data.resources.reverse());
        state.resourceIds = data.resources.map(({ res_id }) => res_id);
      } else if (data.type === "LIST_UPDATE") {
        if (state.resourceIds.includes(data.resource.res_id)) {
          updateListItem(listName, data.resource);
        }
      } else if (data.type === "LIST_ADD") {
        addListItem(listName, data.resource);
        state.resourceIds = [data.resource.res_id, ...state.resourceIds];
      } else if (data.type === "LIST_REMOVE") {
        removeListItem(listName, data.res_id);
        state.resourceIds = state.resourceIds.filter(
          (id) => id !== data.res_id,
        );
      }
    });
    if (additionalMessageHandler) {
      socket.addEventListener("message", additionalMessageHandler);
    }
  });
}

export function setupValidationListeners(socket) {
  // Note: This mapping gets mutated.
  const msgElements = {};

  const setupInputs = (dataPoints) => {
    for (const [dataPoint, _val] of Object.entries(dataPoints)) {
      const msgEl = validationMsgField(dataPoint);
      const infoEl = infoField(dataPoint);
      if (!msgEl || infoEl) {
        console.debug(`Missing msg element for ${dataPoint}`);
        continue;
      }

      // Clear any stale validation messages.
      msgEl.textContent = "";

      msgElements[dataPoint] = msgEl;
    }
  };

  socket.addEventListener("message", (ev) => {
    /** @type ValidationMsg */
    const data = JSON.parse(ev.data);
    if (data.type === "INIT_VALIDATION") {
      setupInputs(data.fields);
    } else if (data.type === "VALIDATION") {
      for (const msgEl of Object.values(msgElements)) {
        // Clear previous validation messages;
        msgEl.textContent = "";
      }

      for (const [dataPoint, msg] of data.success_messages) {
        const msgEl = msgElements[dataPoint];
        msgEl.style.color = "green";
        msgEl.textContent = msg;
      }

      for (const [dataPoint, msg] of data.failure_messages) {
        const msgEl = msgElements[dataPoint];
        msgEl.style.color = "red";
        msgEl.textContent = msg;
      }
    }
  });
}
