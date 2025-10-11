import { listSocketFactory } from "../../editing.mjs";
import { onPageLoad } from "../../utils.mjs";

onPageLoad(async () => {
  const listFactory = listSocketFactory("members", "member");
  listFactory();
});
