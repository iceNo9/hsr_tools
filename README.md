# hsr_tools
星穹铁道辅助工具

<!-- 坐标数据构建 -->
box类
{
    name:""
    resolution:(1920,1080)
    position_start:(x,y)
    position_end:(x,y)

    方法:格式化输出[x1,x2,y1,y2]
}

坐标管理类
{
    resolution:(1920,1080)
    box_list{
        name1:box类
        name2:box类
        ...
    }

    方法:导出到json
    方法:导入json
    方法:根据box类的resolution和自己的resolution,重新格式化输出[x1,x2,y1,y2],等比例
}

<!-- 遗器数据构建 -->
遗器类
{
    name:"",
    location":""
    level:0
    item_number:0
    item_detail:{
        main:{
            name:value
        }
        sub:
        {
            name:value
            ...
        }
    }
    from_set:""
}
