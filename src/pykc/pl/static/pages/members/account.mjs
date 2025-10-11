import { onPageLoad } from "../../utils.mjs";
import { editSocketFactory } from "../../editing.mjs";

onPageLoad(() => {
  const openSocket = editSocketFactory("members", "account");
  openSocket();
});
