2026-10-24 内容覆盖与阅读顺序检查

coverage.json：CS2680与Dive into LLMs的覆盖对照、版本边界和新增位置。
cs2680-implementation.json、dive-implementation.json、root-implementation.json：新增内容记录。
cross-review.json、dive-cross-review.json：新增机制与算例的独立交叉检查。
../numbering-map.json：统一课号、作业号及题号与原文件/锚点的映射。
../numbering-update.json：35处后续前置链接与38处旧编号引用的修正记录。
navigation-fix.json：作业05在目录、侧栏及原有主线顺序中的一致性修复。
static-results.json：95页HTML、18,947处本地引用及派生正文一致性检查。
regression-results.json 与 *-tests.log：216项既有测试的本轮运行结果。
../../checks/coverage_numeric.py 与 ../../checks/coverage_numeric_results.json：26项新增教学算例与复算结果。
browser-results.json：真实file://离线环境中的36种页面/宽度组合与15项交互检查。
retention-results.json：原资料文件、模型源码、数据和10幅必要图解的保留检查。
derived-build.json：连续阅读版、Markdown与全文搜索的重建记录。

build_course.py 用于从94份规范网页正文重建 complete.html、wiki/ 与搜索数据。
需要 Python 及 beautifulsoup4、lxml、markdownify；先修改分章HTML，再运行重建。
validate_package.py 用于检查上述派生内容、主线顺序、本地引用和编号的一致性。
renumber_course.py 为此次迁移的保留脚本，已运行完成；不要重复迁移当前资料包。

范围说明
此目录是本次检查的当前记录。其他 validation/、editorial/content-review/ 等目录仍保留历史证据。
数值复算用于核对教学公式与边界；没有把理想化算例当作GPU或大型模型的实测指标。
CS2680按2026-10-24可获取的公开课程资料检查；其未来课程安排不等于已发布讲义。
Dive into LLMs固定核对提交 f84c04268794ef94f8949808bbc14ab8636763a0。
旧教程依赖版本保留为历史复现条件，不作为当前安装建议；未执行其全部代码或视频内容。
