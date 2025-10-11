import { listSocketFactory } from "../../editing.mjs";
import { onPageLoad } from "../../utils.mjs";

onPageLoad(async () => {
  const appName = "events";
  const venueListName = "venue";

  const venueFactory = listSocketFactory(appName, venueListName);

  // Initialize Sockets
  venueFactory();
});
