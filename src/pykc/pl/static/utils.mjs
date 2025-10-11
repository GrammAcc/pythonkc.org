// @ts-check

import { closeSocket } from "./sockets.mjs";

/** Bind some JS code to run on page load.
 * @param {function} callback A 0-arity function to call once the page content is loaded.
 */
export const onPageLoad = (callback) => {
  if (document.readyState !== "loading") {
    callback();
  } else {
    document.addEventListener("DOMContentLoaded", () => {
      callback();
    });
  }
};

/**
 * @param {string} s
 * @returns {string}
 */
export function hyphenToSnake(s) {
  // @ts-expect-error [2550]
  return s.replaceAll("-", "_");
}

/**
 * @param {string} s
 * @returns {string}
 */
export function snakeToHyphen(s) {
  // @ts-expect-error [2550]
  return s.replaceAll("_", "-");
}

/**
 * @template T
 * @param {T} val
 * @returns {NonNullable<T>}
 */
export function assert(val) {
  if (val === null || val === undefined) {
    throw new Error("assertion failed");
  } else {
    return val;
  }
}
