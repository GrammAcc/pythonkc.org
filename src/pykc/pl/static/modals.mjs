import { assert } from "./utils.mjs";

/**
 * @param {string} resName
 * @returns {HTMLDialogElement}
 */
export function makeModal(resName) {
  const targetModal = getModal(resName);

  const saveBtn = document.createElement("button");
  saveBtn.id = `${resName}-submit-btn`;
  saveBtn.classList.add("action-btn");
  saveBtn.textContent = "Save";

  const closeBtn = document.createElement("button");
  closeBtn.classList.add("action-btn");
  closeBtn.textContent = "Close";

  closeBtn.addEventListener("click", (_ev) => targetModal.close());

  const actions = document.createElement("div");
  actions.classList.add("bookends");
  actions.appendChild(saveBtn);
  actions.appendChild(closeBtn);

  targetModal.appendChild(actions);

  return targetModal;
}

/**
 * @param {string} elId
 * @param {string} displayText
 * @returns {HTMLButtonElement}
 */
const makeActionBtn = (displayText) => {
  const newBtn = document.createElement("button");
  newBtn.classList.add("action-btn");
  newBtn.textContent = displayText;
  return newBtn;
};

/**
 * @param {HTMLDialogElement} modalEl
 * @param {string} displayText
 * @returns {HTMLButtonElement}
 */
export function makeModalBtn(modalEl, displayText) {
  const openBtn = makeActionBtn(displayText);
  openBtn.addEventListener("click", () => modalEl.showModal());
  return openBtn;
}

/**
 * @param {string} resName
 * @returns {HTMLDialogElement}
 */
export function getModal(resName) {
  return assert(document.querySelector(`#${resName}-modal`));
}

export function makeConfirmModal(confirmText, onConfirm) {
  const modal = document.createElement("dialog");
  modal.classList.add("modal");
  const msgEl = document.createElement("p");
  msgEl.textContent = confirmText;
  modal.appendChild(msgEl);
  const confirmBtn = makeActionBtn("Confirm");
  const cancelBtn = makeActionBtn("Cancel");

  confirmBtn.addEventListener("click", async (_ev) => {
    await onConfirm();
    modal.close();
  });

  cancelBtn.addEventListener("click", (_ev) => {
    modal.close();
  });

  const actions = document.createElement("div");
  actions.classList.add("bookends");
  actions.appendChild(confirmBtn);
  actions.appendChild(cancelBtn);
  modal.appendChild(actions);
  const anchor = document.querySelector("main");
  anchor.appendChild(modal);
  return modal;
}
