import { editSocketFactory } from "../../editing.mjs";
import { onPageLoad } from "../../utils.mjs";

onPageLoad(() => {
  const openSocket = editSocketFactory("events", "recurring");
  openSocket();
});
