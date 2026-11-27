"""Private prepared validation: definitions only until an exact runtime grant.

One fixed donor pair is embedded byte-for-byte so the test is independent of
external output directories. It is expected/input material, never a producer.
The integration case starts the actual production Coordinator/worker and owns
its temporary SQLite database. It does not inject Coordinator readiness or
import any test Harness.
"""

import base64
import hashlib
import json
import os
import sys
import tracemalloc

import pytest
from ontolearn_engine import storage_probe

INPUT_B64 = (
    "ewogICJzY2hlbWEiOiAidDA5LmdiYXNlLWJlbmNobWFyay1pbnB1dC92MSIsCiAgInNjYWxlIjogMSwKICAic291cmNlR0Jh"
    "c2VTaGEyNTYiOiAiMzA2ZDQxYjMzMmQyMjNiNDc5MjllYjkwZjE5NmM3MWU0OTY1YTBlOWZmODExMDBjOTQ2OWVkMzI2MTJl"
    "ODg0NSIsCiAgInF1ZXJ5U2hhMjU2IjogIjhlZmJhY2Q1ODljNDJhYzQwYWJiYjU1NDc1Y2RkMDg4ZTQwN2E4OGEyM2UwZGI2"
    "MWRjODM3NWUwNGU0ZGQzODYiLAogICJzY2FsZURlZmluaXRpb24iOiAiMTgqTiBhc3NlcnRlZCB0cmlwbGVzLCBzaGFyZWQg"
    "MTAgb250b2xvZ3kgdHJpcGxlczsgZGF0YSBzY2FsZSwgbm90IHNjaGVtYSBzY2FsZSIsCiAgIm9udG9sb2d5IjogWwogICAg"
    "ewogICAgICAic3ViamVjdCI6ICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOkVxdWlwbWVudCIsCiAgICAgICJwcmVkaWNhdGUi"
    "OiAiaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zI3R5cGUiLAogICAgICAib2JqZWN0IjogIjxo"
    "dHRwOi8vd3d3LnczLm9yZy8yMDAyLzA3L293bCNDbGFzcz4iCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1cm46"
    "b250b2xlYXJuOmxlYXJuaW5nOkFsYXJtIiwKICAgICAgInByZWRpY2F0ZSI6ICJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAy"
    "LzIyLXJkZi1zeW50YXgtbnMjdHlwZSIsCiAgICAgICJvYmplY3QiOiAiPGh0dHA6Ly93d3cudzMub3JnLzIwMDIvMDcvb3ds"
    "I0NsYXNzPiIKICAgIH0sCiAgICB7CiAgICAgICJzdWJqZWN0IjogInVybjpvbnRvbGVhcm46bGVhcm5pbmc6V29ya09yZGVy"
    "IiwKICAgICAgInByZWRpY2F0ZSI6ICJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjdHlwZSIs"
    "CiAgICAgICJvYmplY3QiOiAiPGh0dHA6Ly93d3cudzMub3JnLzIwMDIvMDcvb3dsI0NsYXNzPiIKICAgIH0sCiAgICB7CiAg"
    "ICAgICJzdWJqZWN0IjogInVybjpvbnRvbGVhcm46bGVhcm5pbmc6SGlnaFJpc2tFcXVpcG1lbnQiLAogICAgICAicHJlZGlj"
    "YXRlIjogImh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyN0eXBlIiwKICAgICAgIm9iamVjdCI6"
    "ICI8aHR0cDovL3d3dy53My5vcmcvMjAwMi8wNy9vd2wjQ2xhc3M+IgogICAgfSwKICAgIHsKICAgICAgInN1YmplY3QiOiAi"
    "dXJuOm9udG9sZWFybjpsZWFybmluZzpuYW1lIiwKICAgICAgInByZWRpY2F0ZSI6ICJodHRwOi8vd3d3LnczLm9yZy8xOTk5"
    "LzAyLzIyLXJkZi1zeW50YXgtbnMjdHlwZSIsCiAgICAgICJvYmplY3QiOiAiPGh0dHA6Ly93d3cudzMub3JnLzIwMDIvMDcv"
    "b3dsI0RhdGF0eXBlUHJvcGVydHk+IgogICAgfSwKICAgIHsKICAgICAgInN1YmplY3QiOiAidXJuOm9udG9sZWFybjpsZWFy"
    "bmluZzpsZXZlbCIsCiAgICAgICJwcmVkaWNhdGUiOiAiaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4"
    "LW5zI3R5cGUiLAogICAgICAib2JqZWN0IjogIjxodHRwOi8vd3d3LnczLm9yZy8yMDAyLzA3L293bCNEYXRhdHlwZVByb3Bl"
    "cnR5PiIKICAgIH0sCiAgICB7CiAgICAgICJzdWJqZWN0IjogInVybjpvbnRvbGVhcm46bGVhcm5pbmc6c3RhdHVzIiwKICAg"
    "ICAgInByZWRpY2F0ZSI6ICJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjdHlwZSIsCiAgICAg"
    "ICJvYmplY3QiOiAiPGh0dHA6Ly93d3cudzMub3JnLzIwMDIvMDcvb3dsI0RhdGF0eXBlUHJvcGVydHk+IgogICAgfSwKICAg"
    "IHsKICAgICAgInN1YmplY3QiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzphbGFybSIsCiAgICAgICJwcmVkaWNhdGUiOiAi"
    "aHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zI3R5cGUiLAogICAgICAib2JqZWN0IjogIjxodHRw"
    "Oi8vd3d3LnczLm9yZy8yMDAyLzA3L293bCNPYmplY3RQcm9wZXJ0eT4iCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6"
    "ICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOndvcmtPcmRlclN0YXR1cyIsCiAgICAgICJwcmVkaWNhdGUiOiAiaHR0cDovL3d3"
    "dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zI3R5cGUiLAogICAgICAib2JqZWN0IjogIjxodHRwOi8vd3d3Lncz"
    "Lm9yZy8yMDAyLzA3L293bCNEYXRhdHlwZVByb3BlcnR5PiIKICAgIH0sCiAgICB7CiAgICAgICJzdWJqZWN0IjogInVybjpv"
    "bnRvbGVhcm46bGVhcm5pbmc6ZXZlbnRPcmRlciIsCiAgICAgICJwcmVkaWNhdGUiOiAiaHR0cDovL3d3dy53My5vcmcvMTk5"
    "OS8wMi8yMi1yZGYtc3ludGF4LW5zI3R5cGUiLAogICAgICAib2JqZWN0IjogIjxodHRwOi8vd3d3LnczLm9yZy8yMDAyLzA3"
    "L293bCNPYmplY3RQcm9wZXJ0eT4iCiAgICB9CiAgXSwKICAiYXNzZXJ0ZWRGYWN0cyI6IFsKICAgIHsKICAgICAgInN1Ympl"
    "Y3QiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzplcXVpcG1lbnQvMDAxIiwKICAgICAgInByZWRpY2F0ZSI6ICJodHRwOi8v"
    "d3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjdHlwZSIsCiAgICAgICJvYmplY3QiOiAiPHVybjpvbnRvbGVh"
    "cm46bGVhcm5pbmc6RXF1aXBtZW50PiIKICAgIH0sCiAgICB7CiAgICAgICJzdWJqZWN0IjogInVybjpvbnRvbGVhcm46bGVh"
    "cm5pbmc6ZXF1aXBtZW50LzAwMSIsCiAgICAgICJwcmVkaWNhdGUiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzpuYW1lIiwK"
    "ICAgICAgIm9iamVjdCI6ICJcIuazteermUFcIiIKICAgIH0sCiAgICB7CiAgICAgICJzdWJqZWN0IjogInVybjpvbnRvbGVh"
    "cm46bGVhcm5pbmc6ZXF1aXBtZW50LzAwMiIsCiAgICAgICJwcmVkaWNhdGUiOiAiaHR0cDovL3d3dy53My5vcmcvMTk5OS8w"
    "Mi8yMi1yZGYtc3ludGF4LW5zI3R5cGUiLAogICAgICAib2JqZWN0IjogIjx1cm46b250b2xlYXJuOmxlYXJuaW5nOkVxdWlw"
    "bWVudD4iCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOmVxdWlwbWVudC8w"
    "MDIiLAogICAgICAicHJlZGljYXRlIjogInVybjpvbnRvbGVhcm46bGVhcm5pbmc6bmFtZSIsCiAgICAgICJvYmplY3QiOiAi"
    "XCLms7Xnq5lCXCIiCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOmVxdWlw"
    "bWVudC8wMDMiLAogICAgICAicHJlZGljYXRlIjogImh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1u"
    "cyN0eXBlIiwKICAgICAgIm9iamVjdCI6ICI8dXJuOm9udG9sZWFybjpsZWFybmluZzpFcXVpcG1lbnQ+IgogICAgfSwKICAg"
    "IHsKICAgICAgInN1YmplY3QiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzplcXVpcG1lbnQvMDAzIiwKICAgICAgInByZWRp"
    "Y2F0ZSI6ICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOm5hbWUiLAogICAgICAib2JqZWN0IjogIlwi5aSH55So5rO1Q1wiIgog"
    "ICAgfSwKICAgIHsKICAgICAgInN1YmplY3QiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzphbGFybS9BMDEiLAogICAgICAi"
    "cHJlZGljYXRlIjogImh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyN0eXBlIiwKICAgICAgIm9i"
    "amVjdCI6ICI8dXJuOm9udG9sZWFybjpsZWFybmluZzpBbGFybT4iCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1"
    "cm46b250b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMSIsCiAgICAgICJwcmVkaWNhdGUiOiAidXJuOm9udG9sZWFybjpsZWFy"
    "bmluZzpsZXZlbCIsCiAgICAgICJvYmplY3QiOiAiXCJIaWdoXCIiCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1"
    "cm46b250b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMSIsCiAgICAgICJwcmVkaWNhdGUiOiAidXJuOm9udG9sZWFybjpsZWFy"
    "bmluZzpzdGF0dXMiLAogICAgICAib2JqZWN0IjogIlwiT3BlblwiIgogICAgfSwKICAgIHsKICAgICAgInN1YmplY3QiOiAi"
    "dXJuOm9udG9sZWFybjpsZWFybmluZzplcXVpcG1lbnQvMDAxIiwKICAgICAgInByZWRpY2F0ZSI6ICJ1cm46b250b2xlYXJu"
    "OmxlYXJuaW5nOmFsYXJtIiwKICAgICAgIm9iamVjdCI6ICI8dXJuOm9udG9sZWFybjpsZWFybmluZzphbGFybS9BMDE+Igog"
    "ICAgfSwKICAgIHsKICAgICAgInN1YmplY3QiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzphbGFybS9BMDIiLAogICAgICAi"
    "cHJlZGljYXRlIjogImh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyN0eXBlIiwKICAgICAgIm9i"
    "amVjdCI6ICI8dXJuOm9udG9sZWFybjpsZWFybmluZzpBbGFybT4iCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1"
    "cm46b250b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMiIsCiAgICAgICJwcmVkaWNhdGUiOiAidXJuOm9udG9sZWFybjpsZWFy"
    "bmluZzpsZXZlbCIsCiAgICAgICJvYmplY3QiOiAiXCJIaWdoXCIiCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1"
    "cm46b250b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMiIsCiAgICAgICJwcmVkaWNhdGUiOiAidXJuOm9udG9sZWFybjpsZWFy"
    "bmluZzpzdGF0dXMiLAogICAgICAib2JqZWN0IjogIlwiQ2xvc2VkXCIiCiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6"
    "ICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOmVxdWlwbWVudC8wMDIiLAogICAgICAicHJlZGljYXRlIjogInVybjpvbnRvbGVh"
    "cm46bGVhcm5pbmc6YWxhcm0iLAogICAgICAib2JqZWN0IjogIjx1cm46b250b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMj4i"
    "CiAgICB9LAogICAgewogICAgICAic3ViamVjdCI6ICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMyIsCiAgICAg"
    "ICJwcmVkaWNhdGUiOiAiaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zI3R5cGUiLAogICAgICAi"
    "b2JqZWN0IjogIjx1cm46b250b2xlYXJuOmxlYXJuaW5nOkFsYXJtPiIKICAgIH0sCiAgICB7CiAgICAgICJzdWJqZWN0Ijog"
    "InVybjpvbnRvbGVhcm46bGVhcm5pbmc6YWxhcm0vQTAzIiwKICAgICAgInByZWRpY2F0ZSI6ICJ1cm46b250b2xlYXJuOmxl"
    "YXJuaW5nOmxldmVsIiwKICAgICAgIm9iamVjdCI6ICJcIkxvd1wiIgogICAgfSwKICAgIHsKICAgICAgInN1YmplY3QiOiAi"
    "dXJuOm9udG9sZWFybjpsZWFybmluZzphbGFybS9BMDMiLAogICAgICAicHJlZGljYXRlIjogInVybjpvbnRvbGVhcm46bGVh"
    "cm5pbmc6c3RhdHVzIiwKICAgICAgIm9iamVjdCI6ICJcIk9wZW5cIiIKICAgIH0sCiAgICB7CiAgICAgICJzdWJqZWN0Ijog"
    "InVybjpvbnRvbGVhcm46bGVhcm5pbmc6ZXF1aXBtZW50LzAwMyIsCiAgICAgICJwcmVkaWNhdGUiOiAidXJuOm9udG9sZWFy"
    "bjpsZWFybmluZzphbGFybSIsCiAgICAgICJvYmplY3QiOiAiPHVybjpvbnRvbGVhcm46bGVhcm5pbmc6YWxhcm0vQTAzPiIK"
    "ICAgIH0KICBdLAogICJxdWVyeVRleHQiOiAiUFJFRklYIGw6IDx1cm46b250b2xlYXJuOmxlYXJuaW5nOj5cblNFTEVDVCA/"
    "YWxhcm0gV0hFUkUgeyA/ZXF1aXBtZW50IGEgbDpFcXVpcG1lbnQgOyBsOmFsYXJtID9hbGFybSAuID9hbGFybSBsOmxldmVs"
    "IFwiSGlnaFwiIDsgbDpzdGF0dXMgXCJPcGVuXCIgLiB9IE9SREVSIEJZID9hbGFybVxuIiwKICAiY29waWVzIjogWwogICAg"
    "ewogICAgICAicmVwbGljYSI6IDAsCiAgICAgICJpcmlNYXBwaW5nIjogewogICAgICAgICJ1cm46b250b2xlYXJuOmxlYXJu"
    "aW5nOmVxdWlwbWVudC8wMDEiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzplcXVpcG1lbnQvMDAxIiwKICAgICAgICAidXJu"
    "Om9udG9sZWFybjpsZWFybmluZzplcXVpcG1lbnQvMDAyIjogInVybjpvbnRvbGVhcm46bGVhcm5pbmc6ZXF1aXBtZW50LzAw"
    "MiIsCiAgICAgICAgInVybjpvbnRvbGVhcm46bGVhcm5pbmc6ZXF1aXBtZW50LzAwMyI6ICJ1cm46b250b2xlYXJuOmxlYXJu"
    "aW5nOmVxdWlwbWVudC8wMDMiLAogICAgICAgICJ1cm46b250b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMSI6ICJ1cm46b250"
    "b2xlYXJuOmxlYXJuaW5nOmFsYXJtL0EwMSIsCiAgICAgICAgInVybjpvbnRvbGVhcm46bGVhcm5pbmc6YWxhcm0vQTAyIjog"
    "InVybjpvbnRvbGVhcm46bGVhcm5pbmc6YWxhcm0vQTAyIiwKICAgICAgICAidXJuOm9udG9sZWFybjpsZWFybmluZzphbGFy"
    "bS9BMDMiOiAidXJuOm9udG9sZWFybjpsZWFybmluZzphbGFybS9BMDMiCiAgICAgIH0KICAgIH0KICBdLAogICJydW50aW1l"
    "UHJvdmlkZXJSZXNvdXJjZSI6IGZhbHNlLAogICJleGNsdWRlZCI6ICJObyBpbmZlcnJlZCBmYWN0cywgcmVzdWx0cywgREIv"
    "cHJvamVjdCBpZGVudGl0eSwgcnVsZS9iZWhhdmlvci9zY2VuYXJpbyBleGVjdXRpb24gb3IgbWFwcGVkIG93bmVyc2hpcCIK"
    "fQo="
)

EXPECTED_B64 = (
    "ewogICJzY2hlbWEiOiAidDA5LmdiYXNlLWJlbmNobWFyay1leHBlY3RlZC92MSIsCiAgInNjYWxlIjogMSwKICAicm9sZSI6"
    "ICJFWFBFQ1RFRF9PTkxZX05PVF9NRUFTVVJFRCIsCiAgImZvcm11bGEiOiAiZmFjdHM9MTgqTjsgb250b2xvZ3k9MTA7IGdy"
    "YXBoPTE4Kk4rMTA7IFEwMT1OIiwKICAiY291bnRzIjogewogICAgImVxdWlwbWVudCI6IDMsCiAgICAiYWxhcm1zIjogMywK"
    "ICAgICJpbmRpdmlkdWFsSVJJcyI6IDYsCiAgICAiZXF1aXBtZW50QWxhcm1SZWxhdGlvbnMiOiAzLAogICAgImFzc2VydGVk"
    "VHJpcGxlcyI6IDE4LAogICAgInNoYXJlZE9udG9sb2d5VHJpcGxlcyI6IDEwLAogICAgImdyYXBoVHJpcGxlcyI6IDI4LAog"
    "ICAgInF1ZXJ5Um93cyI6IDEKICB9LAogICJxdWVyeSI6IHsKICAgICJ2YXJpYWJsZXMiOiBbCiAgICAgICJhbGFybSIKICAg"
    "IF0sCiAgICAicm93cyI6IFsKICAgICAgewogICAgICAgICJhbGFybSI6ICI8dXJuOm9udG9sZWFybjpsZWFybmluZzphbGFy"
    "bS9BMDE+IgogICAgICB9CiAgICBdCiAgfSwKICAiZGVyaXZhdGlvbiI6ICJPbmUgQTAxIEhpZ2gvT3BlbiBwZXIgaW5kZXBl"
    "bmRlbnQgcmVwbGljYS4gQTAyIENsb3NlZC9BMDMgTG93IG11c3Qgbm90IG9jY3VyLiBTY2hlbWEgdm9jYWJ1bGFyeSByZW1h"
    "aW5zIHNoYXJlZC4iCn0K"
)


@pytest.fixture
def prepared_pair(tmp_path):
    input_path, expected_path = tmp_path / "input.json", tmp_path / "expected.json"
    input_path.write_bytes(base64.b64decode(INPUT_B64, validate=True))
    expected_path.write_bytes(base64.b64decode(EXPECTED_B64, validate=True))
    assert len(input_path.read_bytes()) == 6266
    assert hashlib.sha256(input_path.read_bytes()).hexdigest() == (
        "cf28104cd1e08bed57fb01782e3cb6fde2a10b535c5218e53e8450982d85f93c"
    )
    assert len(expected_path.read_bytes()) == 663
    assert hashlib.sha256(expected_path.read_bytes()).hexdigest() == (
        "347630e2fb39b3c57f00ad5774356fb7d06178a55dfd327eeed84387b3b12140"
    )
    return input_path, expected_path


@pytest.mark.parametrize("scale", [True, 0, 2, 1000, "1"])
def test_prepared_unknown_scale_is_not_a_legacy_fallback(prepared_pair, scale):
    with pytest.raises(storage_probe._PreparedFault, match="fixed-scale-required"):
        storage_probe._prepared_inputs(scale, *prepared_pair)


def test_prepared_pair_is_exact_and_expected_never_produces(prepared_pair):
    data, expected, pins = storage_probe._prepared_inputs(1, *prepared_pair)
    assert len(data["assertedFacts"]) == 18 and len(data["ontology"]) == 10
    assert len(data["queryText"].encode()) == 162
    assert len(data["queryText"].removesuffix("\n").encode()) == 161
    assert expected == {
        "type": "SELECT",
        "variables": ["alarm"],
        "rows": [["<urn:ontolearn:learning:alarm/A01>"]],
    }
    assert [p["bytes"] for p in pins] == [6266, 663]
    with pytest.raises(storage_probe._PreparedFault, match="fixed-pair-mismatch"):
        storage_probe._prepared_inputs(10, *prepared_pair)
    with pytest.raises(storage_probe._PreparedFault, match="fixed-pair-mismatch"):
        storage_probe._prepared_inputs(1, prepared_pair[1], prepared_pair[0])
    original = prepared_pair[0].read_bytes()
    prepared_pair[0].write_bytes(original[:-1] + b" ")
    with pytest.raises(storage_probe._PreparedFault, match="fixed-pair-mismatch"):
        storage_probe._prepared_inputs(1, *prepared_pair)


def test_prepared_existing_profiler_rejected_without_replacing_it(prepared_pair):
    def observer(frame, event, arg):
        return None

    previous = sys.getprofile()
    sys.setprofile(observer)
    try:
        with pytest.raises(storage_probe._PreparedFault, match="existing-profiler"):
            storage_probe.measure_prepared(1, 0, *prepared_pair)
        assert sys.getprofile() is observer
    finally:
        sys.setprofile(previous)


def test_prepared_existing_tracemalloc_rejected_without_stopping_it(prepared_pair):
    assert not tracemalloc.is_tracing()
    tracemalloc.start()
    try:
        with pytest.raises(storage_probe._PreparedFault, match="existing-tracemalloc"):
            storage_probe.measure_prepared(1, 0, *prepared_pair)
        assert tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()


def test_prepared_real_format3_full_diff_job_reopen_and_original_core(prepared_pair):
    # No monkeypatch, readiness token, artificial authority, or direct commit.
    before_profile = sys.getprofile()
    result = storage_probe.measure_prepared(1, 0, *prepared_pair)
    if os.name == "nt":
        assert result["status"] == "measurement-failed"
        assert result["failure"] == {
            "type": "_PreparedFault",
            "reason": "prepared-stdio-platform-not-supplied",
            "detail": None,
        }
        assert result["actualMeasurementCommand"] is None
        assert not {
            "workflow",
            "wire",
            "measurement",
            "actualQuery",
            "producerFirst",
            "producerWarm",
            "persisted",
        }.intersection(result)
        assert sys.getprofile() is before_profile
        assert not tracemalloc.is_tracing()
        return
    assert result["status"] == "observed", json.dumps(result, ensure_ascii=False)
    assert sys.getprofile() is before_profile
    assert not tracemalloc.is_tracing()
    assert result["actualMeasurementCommand"] is None
    workflow, wire = result["workflow"], result["wire"]
    assert workflow["openedBlank"]["formatVersion"] == 3
    assert workflow["openedBlank"]["projectRevision"] == 0
    assert workflow["created"]["receipt"]["projectId"] == workflow["project"]
    assert workflow["queryJob"]["state"] == "succeeded"
    assert workflow["queryJob"]["input"]["scope"] == "asserted"
    assert workflow["queryJob"]["input"]["derivedResultIds"] == []
    assert workflow["queryJob"]["input"]["preparedPlanRef"] is None
    assert result["snapshotId"] == workflow["queryJob"]["inputSnapshotId"]
    assert result["finalCounts"] == {"facts": 18, "ontology": 10, "definitions": 11}
    assert result["resourceQuery"]["bytes"] == 162 and result["managedQuery"]["bytes"] == 161
    assert (
        result["actualQuery"]
        == result["expectedQuery"]
        == {
            "type": "SELECT",
            "variables": ["alarm"],
            "rows": [["<urn:ontolearn:learning:alarm/A01>"]],
        }
    )
    assert wire["naturalExitCode"] == wire["observedExitCode"] == 0
    assert wire["coordinatorPid"] > 0 and wire["coordinatorPid"] != result["probePid"]
    assert wire["fullEof"] == {"stdout": True, "stderr": True}
    assert wire["signals"] == [] and wire["droppedBytes"] == 0
    assert wire["readFailure"] is None and wire["firstChildFailure"] is None
    assert wire["workerPid"] is None and wire["workerPhaseMemory"] is None
    assert all(r["requestBytes"] <= 262144 for r in wire["requests"])
    methods = [r["request"]["method"] for r in wire["requests"]]
    assert methods.count("changeset.preview") == methods.count("changeset.confirm") == 2
    assert methods.count("job.create") == 3
    assert methods.count("query.execution.prepare") == 1
    assert len(workflow["commits"]) == 2
    for committed in workflow["commits"]:
        assert committed["job"]["state"] == "succeeded"
        assert committed["job"]["commitProgress"]["mode"] == "atomic"
        assert committed["marker"]["jobId"] == committed["job"]["jobId"]
        assert committed["marker"]["operationId"] == committed["job"]["operationId"]
        assert committed["receipt"]["kind"] == "receipt"
        assert committed["manifest"]["segmentCount"] >= 1
        assert committed["diff"]
    for run in ("firstCoreCall", "sameProcessRepeat"):
        measured = result["measurement"][run]
        assert measured["counts"] == [1, 2, 1]
        assert measured["profileRestored"] is True
        assert measured["executePeakBytes"] is None
        assert [p["phase"] for p in measured["phases"]] == [
            "factsBuild",
            "ontologyBuild",
            "completeQuery",
        ]
        assert [p["triples"] for p in measured["phases"][:2]] == [18, 10]
        assert measured["phases"][2]["rows"] == result["actualQuery"]["rows"]
        assert all(p["sameFrame"] and p["normalReturn"] for p in measured["phases"])
        assert all(
            p["elapsedNs"] >= 0 and p["pythonBytesPeak"] >= p["pythonBytesAfter"]
            for p in measured["phases"]
        )
    for value in (result["producerFirst"], result["producerWarm"]):
        assert value["payload"] == result["persisted"]["payload"]
        assert [(r["ordinal"], r["cells"]) for r in value["rows"]] == [
            (r["ordinal"], r["cells"]) for r in result["persisted"]["rows"]
        ]


# The gold below was computed from the separately fixed scale100 input bytes
# 397210/28ff312af35e79b17c390aa96c477347208f66879a0407e8eb0f7ddf508ee5b8.
# It is not computed from a batcher's output. No external outputs path is needed.
def _independent_prepared_encoding(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _fixed_hundred_manual_facts():
    seed_raw = base64.b64decode(INPUT_B64, validate=True)
    assert hashlib.sha256(seed_raw).hexdigest() == (
        "cf28104cd1e08bed57fb01782e3cb6fde2a10b535c5218e53e8450982d85f93c"
    )
    seed = json.loads(seed_raw)
    expanded = []
    for replica in range(100):
        mapping = {
            iri: iri if replica == 0 else f"{iri}/replica/{replica:06d}"
            for iri in seed["copies"][0]["iriMapping"]
        }
        for fact in seed["assertedFacts"]:
            term = fact["object"]
            object_ = (
                f"<{mapping[term[1:-1]]}>"
                if term.startswith("<") and term.endswith(">") and term[1:-1] in mapping
                else term
            )
            expanded.append(
                {
                    "subject": mapping.get(fact["subject"], fact["subject"]),
                    "predicate": fact["predicate"],
                    "object": object_,
                }
            )
    raw = _independent_prepared_encoding(expanded)
    assert len(expanded) == 1800 and len(raw) == 267686
    assert hashlib.sha256(raw).hexdigest() == (
        "756bff54b923e11d4e9bf2de35d726fd5100bc6ea807d7b3b88ccb354d199bcf"
    )
    return [
        {
            **fact,
            "id": hashlib.sha256(
                _independent_prepared_encoding([fact["subject"], fact["predicate"], fact["object"]])
            ).hexdigest(),
        }
        for fact in expanded
    ]


def _independent_worst_preview(project, facts):
    params = {
        "projectId": project,
        "baseRevision": 9007199254740991,
        "intent": "change",
        "plan": {"manual": facts},
    }
    envelope = {
        "kind": "request",
        "id": "f" * 36,
        "protocolVersion": 3,
        "engineSessionId": "f" * 36,
        "method": "changeset.preview",
        "params": params,
    }
    return params, envelope


def test_prepared_original_record_needs_params_reserve_as_well_as_wire():
    facts = _fixed_hundred_manual_facts()
    project = "e98c9eeb-dcb7-4d9b-bad1-6fa1d31a0695"
    params, envelope = _independent_worst_preview(project, facts[:1186])
    params["baseRevision"] = 1
    envelope["id"] = "db28e385-d032-4964-856b-db5613d4a33a"
    envelope["engineSessionId"] = "064a9e90-18a9-4f5f-9ad5-1ea16c368381"
    params_raw = _independent_prepared_encoding(params)
    wire_raw = _independent_prepared_encoding(envelope)
    # Reconstruct the actual recorded object, not an invented long-ASCII fixture.
    assert len(params_raw) == 261768 and len(wire_raw) == 261946
    assert hashlib.sha256(params_raw).hexdigest() == (
        "4f5027a8c317576fb70766c8449a68aa902c15d5a75a055a47a907bf97b8b643"
    )
    assert hashlib.sha256(wire_raw).hexdigest() == (
        "750817d2efcbcd4d7158e60f0b0bcdaadaa14b271711435ddd402f2b012e5994"
    )
    assert len(facts[:1186]) <= 4096 and len(wire_raw) <= 262144
    assert len(params_raw) + 1024 == 262792 > 262144
    assert not storage_probe._prepared_preview_fits(params, 262144)
    worst_params, worst_envelope = _independent_worst_preview(project, facts[:1186])
    assert len(_independent_prepared_encoding(worst_envelope)) == 261961 <= 262144
    assert len(_independent_prepared_encoding(worst_params)) + 1024 == 262807
    assert not storage_probe._prepared_preview_fits(worst_params, 262144)


@pytest.mark.parametrize("max_frame", [262144, 131072])
def test_prepared_new_batches_keep_both_gates_and_every_original_fact(max_frame):
    facts = _fixed_hundred_manual_facts()
    project = "e98c9eeb-dcb7-4d9b-bad1-6fa1d31a0695"
    batches = list(storage_probe._prepared_fact_batches(project, facts, max_frame))
    assert len(batches) >= 2 and all(batches)
    reconnected = [fact for batch in batches for fact in batch]
    assert reconnected == facts
    assert len(reconnected) == 1800
    assert len({fact["id"] for fact in reconnected}) == 1800
    for batch in batches:
        params, envelope = _independent_worst_preview(project, batch)
        assert len(batch) <= 4096
        assert len(_independent_prepared_encoding(envelope)) <= max_frame
        assert len(_independent_prepared_encoding(params)) + 1024 <= min(262144, max_frame)
        assert storage_probe._prepared_preview_fits(params, max_frame)
    # The next actual fact does not fit the prior batch; no arbitrary data thinning.
    for previous, following in zip(batches, batches[1:], strict=False):
        params, envelope = _independent_worst_preview(project, [*previous, following[0]])
        assert not (
            len(previous) + 1 <= 4096
            and len(_independent_prepared_encoding(envelope)) <= max_frame
            and len(_independent_prepared_encoding(params)) + 1024 <= min(262144, max_frame)
        )


@pytest.mark.parametrize("good_prefix", [False, True])
def test_prepared_new_singleton_cannot_bypass_params_gate(good_prefix):
    facts = _fixed_hundred_manual_facts()
    project = "e98c9eeb-dcb7-4d9b-bad1-6fa1d31a0695"
    too_large = {**facts[0], "object": '"' + "x" * 261000 + '"'}
    params, envelope = _independent_worst_preview(project, [too_large])
    assert len(_independent_prepared_encoding(envelope)) == 261501 <= 262144
    assert len(_independent_prepared_encoding(params)) + 1024 == 262347 > 262144
    original = [facts[0], too_large] if good_prefix else [too_large]
    batches = storage_probe._prepared_fact_batches(project, original, 262144)
    # In the next-batch case even the good prefix cannot be yielded/committed
    # before discovering that the singleton would violate the same two gates.
    with pytest.raises(storage_probe._PreparedFault, match="single-fact-frame-limit"):
        next(batches)
