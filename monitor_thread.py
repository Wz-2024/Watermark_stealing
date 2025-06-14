import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import traceback
import sys
import psutil
import os

def send_email(subject, content):
    # 邮件服务器配置
    mail_host = "smtp.qq.com"  # QQ邮箱服务器
    mail_user = "2459769486@qq.com"  # 发件人邮箱
    mail_pass = "bpygfuwyfsypeced"  # 邮箱授权码，不是登录密码
    
    # 邮件内容
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = mail_user
    message['To'] = "3328889702@qq.com"  # 收件人邮箱
    message['Subject'] = Header(subject, 'utf-8')
    
    try:
        # 连接服务器
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 使用SSL加密
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(mail_user, ["3328889702@qq.com"], message.as_string())
        smtpObj.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def monitor_process(pid):
    try:
        process = psutil.Process(pid)
        print(f"开始监控进程 {pid} ({process.name()})")
        
        while True:
            try:
                # 检查进程是否存在
                if not process.is_running():
                    error_msg = f"进程 {pid} 已停止运行"
                    send_email("进程监控通知", error_msg)
                    print(error_msg)
                    break
                
                # 检查进程状态
                status = process.status()
                if status == psutil.STATUS_ZOMBIE:
                    error_msg = f"进程 {pid} 处于僵尸状态"
                    send_email("进程监控通知", error_msg)
                    print(error_msg)
                    break
                
                # 获取进程资源使用情况
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                print(f"进程 {pid} 状态: CPU使用率 {cpu_percent}%, 内存使用 {memory_info.rss / 1024 / 1024:.2f}MB")
                
                time.sleep(10)  # 每10秒检查一次
                
            except psutil.NoSuchProcess:
                error_msg = f"进程 {pid} 不存在"
                send_email("进程监控通知", error_msg)
                print(error_msg)
                break
            except Exception as e:
                error_msg = f"监控进程 {pid} 时发生错误:\n{str(e)}\n\n堆栈跟踪:\n{traceback.format_exc()}"
                send_email("进程监控通知", error_msg)
                print(error_msg)
                break
                
    except Exception as e:
        error_msg = f"初始化进程监控时发生错误:\n{str(e)}\n\n堆栈跟踪:\n{traceback.format_exc()}"
        send_email("进程监控通知", error_msg)
        print(error_msg)

if __name__ == "__main__":
    # 要监控的进程PID
    target_pid = 1679650
    
    try:
        # 启动监控
        monitor_process(target_pid)
    except KeyboardInterrupt:
        print("监控程序被用户中断") 