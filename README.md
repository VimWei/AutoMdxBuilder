## 一、AutoMdxBuilder 简介

**自动化制作 mdx 词典工具，人人都可以制作电子词典**（支持 Windows/macOS/Linux）

AutoMdxBuilder 是 [[Mdict]](https://www.mdict.cn/wp/?lang=en) 词典制作相关的工具，旨在自动化词典制作过程，同时降低制作门槛，该工具目前具备以下功能：

1. 打包/解包

* 解包 mdx/mdd 文件。功能同 `MdxExport.exe`，支持自动解 mdd 分包，支持保留原始词条顺序。
* 打包成 mdx/mdd 文件。功能同 `MdxBuilder.exe`，支持 mdd 自动分包，支持保留原始词条顺序。

2. 制作词典

* 自动化制作词典 （目前有 A-D 四个可选模板，均支持多卷/集合类型）
* 一键从 PDF/pdg 等原料制作词典

3. 还原词典

* 将 Mdict 词典逆向还原成原材料，方便词典的二次编辑
* 将 Mdict 词典逆向还原成 PDF

4. 其他实用工具

* PDF 与图片互转
* PDF 书签管理

## 二、安装与运行（源码）

1. 安装 [uv](https://docs.astral.sh/uv/)，并在仓库根目录安装依赖：

   ```powershell
   uv sync
   ```

2. 按平台准备：

   - **Windows**：使用 PDF/pdg 相关功能前，将 `FreePic2Pdf/`、`MuPDF/`、`PDFPatcher/`、`Pdg2Pic/` 放入 `tools/`；仅制作、打包、解包词典可不装。
   - **macOS / Linux**：用 `.cross_platform/` 下的 `auto_mdx_builder.py`、`ebook_utils.py` 替换根目录同名文件。

3. 运行：

   ```powershell
   uv run python auto_mdx_builder.py
   ```

   启动后按数字选单操作，例如输入 `20` 生成词典。

## 三、成品预览

### 图像词典 （模板 A，朴素版）
![图像词典 模板 A](images/img_dict_atmpl.gif)

### 图像词典 （模板 B，导航版）
![图像词典 模板 B](images/img_dict_btmpl.gif)

### 文本词典 （模板 C，朴素版）
![文本词典 模板 C](images/text_dict_ctmpl.png)

### 文本词典 （模板 D，导航版）
![文本词典 模板 D](images/text_dict_dtmpl.gif)

## 四、词典制作

### （一） 制作步骤

1. 准备原材料：新建一个文件夹（下称 **amb 文件夹**），放入图片、索引/目录等文件，并放入 `build.toml`（所需文件见「原材料准备」）。
2. 配置 `build.toml`：设置书名、缩写、模板及该模板参数（见「配置文件 `build.toml`」）。
3. 运行程序，在主菜单输入 `20`，按提示输入 amb 文件夹路径或其中的 `build.toml` 路径：

   ```powershell
   uv run python auto_mdx_builder.py
   ```

4. 生成结果输出到 `《书名》_mdict/` 文件夹，内含 `.mdx`、`.mdd` 与 `.css`。

### （二） 原材料准备

使用词典制作功能时，需将原材料集中放入一个 amb 文件夹，配置信息写在其中的 `build.toml`。

示例 amb 文件夹结构：

![amb 文件夹结构](images/amb_folder.png)

制作不同模板所需的原材料不尽相同，下面分模板列举：

**1. 图像词典 （模板 A）**

* （必须） `imgs` 文件夹：存放图像文件，不限定图片格式，png、jpg 等均可，也无特定的名称要求（顺序是对的就行）；
* （可选） `index.txt`: 索引文件
* （可选） `toc.txt`: 目录文件

> index 和 toc 二者中必须至少有一个，如果你的 toc 目录文件比较全，建议改名 toc_all 然后使用模板 B

**2. 图像词典 （模板 B）**

* （必须）`imgs` 文件夹：存放图像文件，同模板 A
* （可选）`index_all.txt`: 全索引文件
* （可选）`toc_all.txt`: 全目录文件
* （可选）`index.txt`: 附加索引文件

> index_all 与 toc_all 是等价的，按偏好使用其中一种即可
> 如果在 index_all 之外还有独立的词条，可以设置 add_extra_index = true, 并将那些词条以 index.txt 文件的形式作为补充

**3. 文本词典 （模板 C）**

* （必须）`index.txt`: 索引文件

**4. 文本词典 （模板 D）**

* （必须）`index_all.txt`: 全索引文件

**【通用可选】** 除上述各模板的材料准备之外，下面两个是通用材料，制作词典可按需添加：

* （可选）`syns.txt` 文件：同义词文件；
* （可选）`info.html` 文件：词典介绍等描述。

**【注意事项】**

* 凡涉及的文本文件（如`.txt`、`.html`），一律要求 **UTF-8 无 BOM** 的编码格式；
* 原材料文件夹中只放置需要用到的文件/文件夹，**为避免误读取，不用到的不要出现在原材料文件夹内**；
* 文件夹和文件的名称就按本说明所提的，不建议自定义名称。

### （三） 原材料文件格式

#### 索引文件 `index.txt`

格式`词目<TAB>页码`（页码数是相对正文起始页的，而不是图片序号）：

![索引文件](images/index.png)

> 如果是多卷模式，则页码需要带分卷号前缀 `[n]` 以标识分卷（第一卷 `[1]` 可以省略不写），比如词条『刘备』是在第 4 卷第 3 页，那么索引应写作 `刘备<TAB>[4]3`；

如果是制作文本词典 （模板 C），用到的文件也叫 `index.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

#### 目录文件 `toc.txt`

格式`[<TAB>*]词目<TAB>页码`，格式大概像这样（行首 TAB 缩进表层级）：

![目录文件](images/toc.png)

格式同程序 `FreePic2Pdf.exe` 的书签文件`FreePic2Pdf_bkmk.txt`，因此也可以直接用 `FreePic2Pdf.exe` 程序从 pdf 文件中导出。

> 与索引文件一样，多卷模式下，页码需要带分卷号前缀 `[n]` 以标识分卷（第一卷 `[1]` 可以省略不写）

#### 全索引文件 `index_all.txt`

是 `index.txt` 的拓展，格式同样是 `词目<TAB>页码` ，只不过 `index_all.txt` 是把 `toc.txt` 也并入进来，并且是严格有序的。

其中目录（章节）的词目要加 `【L《层级》】` 前缀标识，比如顶级章节“正文”前缀就是 `【L0】正文` ，“正文”的下一级“史前篇”的前缀就是 `【L1】史前篇` 。

> 章节词目可以没有对应页码，但要保留 `<TAB>`

![全索引文件](images/index_all.png)

> 与索引文件一样，多卷模式下，页码需要带分卷号前缀 `[n]` 以标识分卷（第一卷 `[1]` 可以省略不写）

如果是制作文本词典 （模板 D），用到的文件也叫 `index_all.txt`，只不过其中的 **页码** 换成了 **词条正文**，格式为 `词目<TAB>词条正文` 。

#### 同义词文件 `syns.txt`

或说重定向文件，格式`同义词<TAB>词目`：

![同义词文件](images/syns.png)

### （四） 配置文件 `build.toml`

可参见 lib/build.toml 中的初始配置，已有详细注释，制作词典时可直接拷贝修改，也可以参考 demo 词典的配置情况。下面选取其中部分作为补充说明：

* `simp_trad_flg`: 是否需要繁简通搜，开启后将会把所有词头都添加繁体/简体跳转，以确保 mdx 使用时能繁简通搜。 默认 false 不开启。
* `multi_volume`: 是否是多卷的，true 则开启多卷模式（需要按多卷模式来准备原材料）。默认是 false 即单卷模式。
* `body_start`: 正文起始图片序号，比如正文第一页是 imgs 文件夹中的第 23 张图，那么就设置为 `body_start = 23`。（多卷模式下该值是列表，比如 `body_start = [23, 19, 1, 1]`）
* `auto_split_columns`: 是否开启自动分栏，设置值 2 则自动分割成两栏，该功能是为方便手机等小屏移动设备的使用而设置。默认值 1 表示不开启自动分栏。
* `body_end_page`: 当自动分栏开启时，该值确定了分栏的应用范围，分栏从正文第一页开启，默认到辞书的最后一页。（多卷模式下该值是列表，比如 `body_end_page = [463, 501, 9999, 9999]`）

对于模板 A 的 `navi_items`，其中 `a` 的值是显示文字，`ref`的值是与 `toc.txt` 中词目对应的：

![settings](images/settings.png)

对于文本词典模板 C,D 中的 `add_headwords` 选项，词条内容如果已经带有标题，可以将该项设置为 false。

### （五） 多卷模式

当在 `build.toml` 中设置 `multi_volume = true` 时，将会按照多卷模式制作词典，这时原材料的命名相比一般模式会有些许不同，下面按模板列举：

图像词典模板 A,B 在多卷模式下，首先图像文件夹结构将是 imgs/vol_01, imgs/vol_02, imgs/vol_03... 即分卷子文件夹名称需加 vol_00 前缀

* 模板 A: 除可以使用全局索引/目录文件 index.txt, toc.txt 外，也可以使用分卷文件 index_01.txt, index_02.txt ... 和 toc_01.txt, toc_02.txt ... （分卷文件中的页码无需加`[n]`前缀）
* 模板 B: 除可以使用全局全索引/全目录文件 index_all.txt/toc_all.txt 外，也可以使用分卷文件 index_all_01.txt, index_all_02.txt ... 或 toc_all_01.txt, toc_all_02.txt ... （分卷文件中的页码无需加`[n]`前缀）
* 模板 D: 同模板 B, 不过因为没有页码，所以分卷文件和全局文件无区别

> 还可以在目录文件、全索引或全目录文件名上标识分卷名称（这样就不用在 `build.toml` 中设置 vol_names 项）, 比如 toc_01_军事卷、 toc_all_01_军事卷.txt 或 index_all_01_军事卷.txt, 这样，程序将会从文件名中读取卷名

## 参考

+ https://github.com/liuyug/mdict-utils
+ https://github.com/VimWei/MdxSourceBuilder
