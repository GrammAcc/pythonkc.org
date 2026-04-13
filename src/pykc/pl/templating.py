import os
from typing import Any

from quart import g
from quart import render_template as quart_render_template

from pykc.constants import (
    App,
    MemberPermissions,
)
from pykc.pl import utils
from pykc.sl import tokens
from pykc.types import RawData


def make_url(url_path: str, *args) -> str:
    site_root = utils.get_domain()
    dynamic_segments = [str(i) for i in args]
    segments = [
        site_root.strip("/"),
        os.environ.get("BASE_URL", "").strip("/"),
        url_path.strip("/"),
        *dynamic_segments,
    ]
    filtered = [i for i in segments if i != ""]
    path = "/".join(filtered).strip("/")
    if path == "":
        return ""
    else:
        return path


def render_template(template_path: str, **kwargs):
    return quart_render_template(
        template_path,
        make_url=make_url,
        csrf_token=tokens.generate_csrf(),
        Permission=MemberPermissions,
        App=App,
        **kwargs,
    )


def in_member_permissions(permission: int) -> bool:
    return g.get("member_permissions", 0) & permission


def enabled_app(app_mask: int) -> bool:
    return utils.is_app_enabled(app_mask)


def make_info(field_name: str, label: str, data: RawData = {}) -> str:
    field_val = data.get(field_name, "")
    return f"""
<span>{label}:
<p id="{field_name}-info" class="info">{field_val}</p>
</span>
"""


def make_input(field_name: str, input_type: str, label: str, data: RawData = {}) -> str:
    field_val = data.get(field_name, "")
    return f"""
<p id="{field_name}-status" class="validation-msg"></p>
<span>{label}:
<input id="{field_name}-input" type="{input_type}" class="common-input" value="{field_val}"></input>
</span>
<p id="{field_name}-validation-msg" class="validation-msg"></p>
"""


def make_textarea(field_name: str, label: str, data: RawData = {}) -> str:
    field_val = data.get(field_name, "")
    return f"""
<p id="{field_name}-status" class="validation-msg"></p>
<span>{label}:
<textarea id="{field_name}-input" class="common-input">{field_val}</textarea>
</span>
<p id="{field_name}-validation-msg" class="validation-msg"></p>
"""


def make_select(
    field_name: str, enum_members: list[tuple[str, Any]], label: str, data: RawData = {}
) -> str:
    current_val = data.get(field_name)
    options = [
        f"""<option {"selected" if current_val == val else ""} value="{val}">{field}</option>"""
        for field, val in enum_members
    ]
    empty_option = """<option value="0">&ltclear selection&gt</option>"""
    option_elements = [empty_option, *options]

    return f"""
<p id="{field_name}-status" class="validation-msg"></p>
<span>{label}:
  <select id="{field_name}-input" class="common-input">
  {"\n".join(option_elements)}
  </select>
</span>
<p id="{field_name}-validation-msg" class="validation-msg"></p>
"""


def make_submit(resource_name: str, button_text: str) -> str:
    return f"""<button id="{resource_name}-submit-btn" class="action-btn">{button_text}</button>"""
