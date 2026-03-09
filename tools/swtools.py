import win32com.client
import pythoncom

def connect_solidworks():
    """连接 SolidWorks 应用程序"""
    try:
        # 设置 COM 线程模型（防止线程错误）
        pythoncom.CoInitialize()
        
        # 正确的 SolidWorks COM 类名：SldWorks.Application（单数）
        sw_app = win32com.client.Dispatch("SldWorks.Application")
        
        # 显示 SolidWorks 窗口（如果后台运行则显示）
        sw_app.Visible = True
        
        # 获取 SolidWorks 版本信息，验证连接成功
        sw_version = sw_app.GetVersion()
        print(f"成功连接 SolidWorks，版本：{sw_version}")
        
        return sw_app
        
    except Exception as e:
        print(f"连接 SolidWorks 失败：{str(e)}")
        # 常见失败原因提示
        print("\n可能的原因：")
        print("1. SolidWorks 未安装或未正确注册 COM 组件")
        print("2. 运行 Python 的用户没有管理员权限")
        print("3. SolidWorks 版本与 pywin32 不兼容")
        print("4. 64位 Python 需对应 64位 SolidWorks")
        return None
sw = connect_solidworks()