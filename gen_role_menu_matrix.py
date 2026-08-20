#!/usr/bin/env python3
"""生成"场地预约"板块的角色-菜单-操作事项权限矩阵 Excel（参照心理中心模板列结构）。"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "场地预约-角色菜单权限矩阵.xlsx")

# 列：板块 | 模块 | 用户 | 流程角色 | 菜单角色 | 系统菜单 | 操作事项 | 完整流程
HEADERS = ["板块", "模块", "用户", "流程角色", "菜单角色", "系统菜单", "操作事项", "完整流程"]

ROWS = [
    # (用户, 流程角色, 菜单角色, 系统菜单, 操作事项)
    (
        "场地管理负责人", "-", "场地管理负责人",
        "1、【数据概览-P】\n2、【场地管理-P】\n3、【表单模板-P】\n4、【预约记录-P】\n5、【待审批-P】\n6、【已审批-P】\n7、【待审批-M】\n8、【已审批-M】",
        "1、在PC端查看全校场地预约数据概览（预约量、热门场地排行、科室预约量、审批效率）\n"
        "2、在PC端新增/编辑/停用场地，配置基础信息、时段策略、表单模板、审批流程、预约权限、预约须知、解说员\n"
        "3、在PC端维护全局表单模板\n"
        "4、在PC端查看、筛选、导出全校预约记录\n"
        "5、在PC/移动端对预约申请进行终审（通过/驳回），处理待办\n"
        "6、在移动端查看已审批历史",
    ),
    (
        "场地负责人", "-", "场地负责人",
        "1、【我负责的场地-P】\n2、【预约记录-P】",
        "1、在PC端查看本人负责的场地列表（仅显示“场地负责人=本人”的场地）\n"
        "2、在PC端编辑本人负责场地的基础信息、时段策略、表单模板、审批流程、预约权限、预约须知\n"
        "3、在PC端新增场地（默认将本人设为负责人）\n"
        "4、在PC端查看本人负责场地的预约记录与使用情况\n"
        "5、无数据概览、全局表单模板等全局菜单权限；社团管理模块按该字段划分数据范围",
    ),
    (
        "综合办管理员", "-", "综合办管理员",
        "1、【数据概览-P】\n2、【场地管理-P】\n3、【表单模板-P】\n4、【预约记录-P】\n5、【待审批-P】\n6、【已审批-P】\n7、【待审批-M】\n8、【已审批-M】",
        "1、在PC端查看本科室场地的预约数据概览\n"
        "2、在PC端维护本科室所辖场地信息及各项配置\n"
        "3、在PC端查看、筛选本科室预约记录\n"
        "4、在PC/移动端审批本科室场地的预约申请（管理员节点）\n"
        "5、在移动端处理待办审批、查看已审批历史",
    ),
    (
        "辅导员", "-", "辅导员",
        "1、【场地预约-P】\n2、【我的预约-P】\n3、【待审批-P】\n4、【已审批-P】\n5、【场地-M】\n6、【我的预约-M】\n7、【待审批-M】\n8、【已审批-M】",
        "1、在PC/移动端浏览场地、查看详情与预约须知\n"
        "2、在PC/移动端发起预约（填写表单、选择时段、阅读须知、选择解说员）\n"
        "3、在PC/移动端查看本人预约及审批进度，取消待审批预约\n"
        "4、在PC/移动端审批所带学生发起的场地预约申请（年级/班级审批节点）\n"
        "5、在移动端处理待办、查看已审批历史",
    ),
    (
        "院系领导", "-", "院系领导",
        "1、【预约记录-P】\n2、【待审批-P】\n3、【已审批-P】\n4、【待审批-M】\n5、【已审批-M】",
        "1、在PC/移动端审批本院系师生的场地预约申请（分支路径中的副书记/二级审批节点）\n"
        "2、在PC端查看本院系场地预约记录\n"
        "3、在移动端处理待办审批、查看已审批历史",
    ),
    (
        "班导师", "-", "班导师",
        "1、【场地预约-P】\n2、【我的预约-P】\n3、【待审批-P】\n4、【已审批-P】\n5、【场地-M】\n6、【我的预约-M】\n7、【待审批-M】\n8、【已审批-M】",
        "1、在PC/移动端浏览场地并发起预约\n"
        "2、在PC/移动端查看本人预约及审批进度\n"
        "3、在PC/移动端审批本班学生发起的场地预约申请（班级审批节点）\n"
        "4、在移动端处理待办、查看已审批历史",
    ),
    (
        "学生", "-", "在学学生",
        "1、【场地预约-P】\n2、【我的预约-P】\n3、【场地-M】\n4、【我的预约-M】",
        "1、在PC/移动端浏览场地、按部门/类型筛选，查看场地详情、规则与预约须知\n"
        "2、在PC/移动端发起预约（填写表单、选择时段、阅读须知并同意、选择解说员）\n"
        "3、在PC/移动端查看本人预约状态与审批进度，取消待审批预约",
    ),
    (
        "学工部职工", "-", "学工部职工",
        "1、【场地预约-P】\n2、【我的预约-P】\n3、【场地-M】\n4、【我的预约-M】",
        "1、在PC/移动端浏览场地并发起预约（职工路径，通常仅需管理员1级审批）\n"
        "2、在PC/移动端查看本人预约及审批进度，取消待审批预约",
    ),
    (
        "导师", "-", "研究生导师",
        "1、【场地预约-P】\n2、【我的预约-P】\n3、【待审批-P】\n4、【已审批-P】\n5、【场地-M】\n6、【我的预约-M】\n7、【待审批-M】\n8、【已审批-M】",
        "1、在PC/移动端浏览场地并发起预约\n"
        "2、在PC/移动端查看本人预约及审批进度\n"
        "3、在PC/移动端审批本人指导研究生发起的场地预约申请（导师审批节点）\n"
        "4、在移动端处理待办、查看已审批历史",
    ),
]

wb = Workbook()
ws = wb.active
ws.title = "场地预约-角色菜单"

thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
header_fill = PatternFill("solid", fgColor="4F46E5")
menu_role_fill = PatternFill("solid", fgColor="DBEAFE")
section_fill = PatternFill("solid", fgColor="F1F5F9")
header_font = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
cell_font = Font(name="微软雅黑", size=10)
bold_font = Font(name="微软雅黑", size=10, bold=True)
top_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)

# 表头
for ci, h in enumerate(HEADERS, 1):
    c = ws.cell(row=1, column=ci, value=h)
    c.fill = header_fill
    c.font = header_font
    c.alignment = center
    c.border = border

# 数据行
start_row = 2
for ri, (user, flow_role, menu_role, menus, ops) in enumerate(ROWS):
    r = start_row + ri
    values = ["场地管理", "场地预约", user, flow_role, menu_role, menus, ops, ""]
    for ci, v in enumerate(values, 1):
        c = ws.cell(row=r, column=ci, value=v)
        c.border = border
        if ci in (6, 7):
            c.font = cell_font
            c.alignment = top_left
        elif ci == 5:
            c.font = bold_font
            c.alignment = center
            c.fill = menu_role_fill
        elif ci == 3:
            c.font = bold_font
            c.alignment = center
        else:
            c.font = cell_font
            c.alignment = center

# 合并"板块""模块"列
last_row = start_row + len(ROWS) - 1
ws.merge_cells(start_row=start_row, start_column=1, end_row=last_row, end_column=1)
ws.merge_cells(start_row=start_row, start_column=2, end_row=last_row, end_column=2)
ws.cell(row=start_row, column=1).fill = section_fill
ws.cell(row=start_row, column=1).font = bold_font
ws.cell(row=start_row, column=1).alignment = center
ws.cell(row=start_row, column=2).alignment = center
ws.cell(row=start_row, column=2).font = bold_font

# 列宽
widths = [10, 10, 14, 9, 14, 26, 60, 16]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

# 行高
ws.row_dimensions[1].height = 24
for ri in range(len(ROWS)):
    ws.row_dimensions[start_row + ri].height = 118

ws.freeze_panes = "A2"
wb.save(OUT)
print("已生成:", OUT)
