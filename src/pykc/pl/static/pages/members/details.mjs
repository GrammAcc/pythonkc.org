import { onPageLoad } from "../../utils.mjs";
import { baseUrl, csrfToken, resourceId } from "../../page-state.mjs";
import { makeConfirmModal } from "../../modals.mjs";

onPageLoad(() => {
  const editRoleDropdown = document.querySelector("#member_permissions-input");
  const submitRoleBtn = document.querySelector("#member_role-submit-btn");

  const submitRoleChange = async () => {
    const memberId = resourceId();
    const newRole = editRoleDropdown.value;
    const patchUrl = `${baseUrl()}/api/v1/members/member/${memberId}/change-role`;
    const res = await fetch(patchUrl, {
      method: "PATCH",
      body: newRole,
      headers: { "X-CSRF-TOKEN": csrfToken(), "Content-Type": "text/plain" },
    });

    if (res.status === 200) {
      alert("member role successfully updated");
    } else {
      alert(
        "update member role failed with unknown error. Please try again later.",
      );
    }
  };

  const changeRoleConfirmModal = makeConfirmModal(
    "This member's role will be changed. Continue?",
    submitRoleChange,
  );

  if (editRoleDropdown && submitRoleBtn) {
    submitRoleBtn.addEventListener("click", (_ev) =>
      changeRoleConfirmModal.showModal(),
    );
  }
});
