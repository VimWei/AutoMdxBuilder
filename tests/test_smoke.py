"""AutoMdxBuilder 冒烟测试。

覆盖最核心、且不依赖 Windows GUI / tools 二进制的路径：
- 程序导入与 Settings 基础路径
- OpenCC 繁简转换
- func_lib 的 index_all -> toc_all 转换
- mdict-utils 打包 / 解包往返

注意：settings.py 以 os.getcwd() 作为 dir_bundle 定位 lib/ 与 _tmp，
因此需在仓库根目录下运行（fixture 会 chdir）。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def amb(monkeypatch):
    """在仓库根目录实例化 AutoMdxBuilder（其 Settings 依赖 cwd）。"""
    monkeypatch.chdir(REPO_ROOT)
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from auto_mdx_builder import AutoMdxBuilder

    return AutoMdxBuilder()


def test_settings_version_and_lib(amb):
    assert amb.settings.version == "1.6"
    assert os.path.isdir(amb.settings.dir_lib)
    assert os.path.isfile(os.path.join(amb.settings.dir_lib, "build.toml"))


def test_opencc_roundtrip():
    from opencc import OpenCC

    assert OpenCC("s2t.json").convert("汉字") == "漢字"
    assert OpenCC("t2s.json").convert("漢字") == "汉字"


def test_index_all_to_toc(amb, tmp_path):
    src = tmp_path / "index_all.txt"
    src.write_text("【L0】正文\t1\n苹果\t1\n", encoding="utf-8")
    out = tmp_path / "toc_all.txt"

    assert amb.func.index_all_to_toc(str(src), str(out)) is True
    text = out.read_text(encoding="utf-8")
    assert "正文" in text
    assert "苹果" in text


def test_mdict_pack_unpack_roundtrip(amb, tmp_path):
    txt = tmp_path / "Smoke.txt"
    txt.write_text(
        'apple\n<link rel="stylesheet" type="text/css" href="smoke.css"/>\n'
        "<div>a fruit</div>\n</>\n"
        'banana\n<link rel="stylesheet" type="text/css" href="smoke.css"/>\n'
        "<div>a fruit</div>\n</>\n",
        encoding="utf-8",
    )
    info = tmp_path / "info.html"
    amb.func.generate_info_html(None, str(info), "Smoke", "B")

    assert amb.utils.pack_to_mdict(str(tmp_path), str(txt), str(info), None) is True

    mdx = tmp_path / "Smoke.mdx"
    assert mdx.is_file()
    assert mdx.stat().st_size > 0

    assert amb.utils.export_mdx(str(mdx)) is True
    exported = (tmp_path / "Smoke" / "Smoke.txt").read_text(encoding="utf-8")
    assert exported.count("</>") == 2
