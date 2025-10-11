import { listSocketFactory } from "../../editing.mjs";
import { onPageLoad } from "../../utils.mjs";

onPageLoad(async () => {
  const appName = "events";
  const upcomingListName = "upcoming_event";
  const pastListName = "past_event";

  const upcomingFactory = listSocketFactory(appName, upcomingListName);
  const pastFactory = listSocketFactory(appName, pastListName);
  const upcomingList = document.querySelector(`#${upcomingListName}-list`);
  const pastList = document.querySelector(`#${pastListName}-list`);

  const upcomingButton = document.querySelector("#upcoming-btn");
  upcomingButton.addEventListener("click", async () => {
    pastList.classList.add("hidden");
    upcomingList.classList.remove("hidden");
  });

  const pastButton = document.querySelector("#past-btn");
  pastButton.addEventListener("click", async () => {
    upcomingList.classList.add("hidden");
    pastList.classList.remove("hidden");
  });

  // Initialize Sockets
  upcomingFactory();
  pastFactory();
});
