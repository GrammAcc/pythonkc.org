// @ts-check

import { baseUrl } from "./page-state.mjs";
import { assert } from "./utils.mjs";

const CLOSED_BY_USER = 4242;
const NORMAL_CLOSE = 1000;
const GOING_AWAY = 1001;
const PROTOCOL_ERROR = 1002;

const nonRetryReasons = [CLOSED_BY_USER, NORMAL_CLOSE, GOING_AWAY];

/**
 * Builds and returns a reconnecting websocket factory function.
 * @param {string} urlPath
 * @param {Array<string>} subprotocols
 * @param {(socket: WebSocket) => void} setup
 *   Callback to execute for additional custom setup on the new websocket.
 *   Can be used to create the message handlers.
 * @returns {() => WebSocket}
 */
export function socketFactory(urlPath, subprotocols, setup) {
  return () => {
    /** @type { WebSocket } */
    let socket;
    const MAX_RETRIES = 5;

    const wsPath = urlPath.startsWith("/") ? urlPath : "/" + urlPath;
    const wsUrl = baseUrl().replace("http", "ws") + "/api/v1" + wsPath;
    const connectSocket = (retryCount) => {
      socket = new WebSocket(wsUrl, subprotocols);

      socket.addEventListener("open", (_ev) => {
        console.info(`WebSocket connected to: ${wsPath}`);
      });

      socket.addEventListener("close", (ev) => {
        if (nonRetryReasons.includes(ev.code)) {
          console.info("websocket successfully closed");
        } else if (ev.code === PROTOCOL_ERROR) {
          console.error("protocol error on socket");
        } else {
          attemptReconnect(retryCount);
        }
      });

      socket.addEventListener("error", (error) => {
        console.error("WebSocket connection error:", error);
        socket.close();
      });

      setup(socket);
    };

    const attemptReconnect = (retryCount) => {
      if (retryCount >= MAX_RETRIES) {
        console.error(
          `Socket error: max retries reached while attempting to reconnect to: ${wsUrl}`,
        );
      } else {
        console.info(`Attempting reconnect to: ${wsUrl}`);
        const backoff = retryCount ** 2 * 1000;
        setTimeout(() => connectSocket(retryCount + 1), backoff);
      }
    };

    connectSocket(0);
    return socket;
  };
}

export function closeSocket(socket) {
  socket.close(CLOSED_BY_USER, "user-initiated");
}

export function socketRef() {
  let socket = null;
  const closer = () => {
    if (socket !== null) {
      closeSocket(socket);
    }
    socket = null;
  };
  const setter = (newSocket) => {
    closer();
    socket = newSocket;
  };
  const getter = () => {
    return assert(socket);
  };
  return [getter, setter, closer];
}
