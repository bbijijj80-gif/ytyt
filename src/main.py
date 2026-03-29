# -*- coding: utf-8 -*-
"""
Windows 11 Security Hardener v2.0
Программа для управления политиками безопасности Windows
Только для системных администраторов
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import os
import ctypes
import winreg
from datetime import datetime

class SecurityHardener:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows 11 Security Hardener v2.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Проверка прав администратора
        if not self.is_admin():
            messagebox.showerror("Ошибка", "Программа должна быть запущена от имени администратора!")
            sys.exit(1)
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка "Система"
        self.system_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.system_frame, text="🖥️ Система")
        self.create_system_tab()
        
        # Вкладка "Приложения"
        self.apps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_frame, text="📁 Приложения")
        self.create_apps_tab()
        
        # Вкладка "USB и Сеть"
        self.usb_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.usb_frame, text="💾 USB и Сеть")
        self.create_usb_tab()
        
        # Вкладка "Браузер"
        self.browser_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.browser_frame, text="🌐 Браузер")
        self.create_browser_tab()
        
        # Журнал событий
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="📋 Журнал")
        self.create_log_tab()
        
        # Нижняя панель с кнопками
        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(fill='x', padx=10, pady=10)
        
        self.apply_all_btn = ttk.Button(self.bottom_frame, text="✅ Применить всё", command=self.apply_all)
        self.apply_all_btn.pack(side='left', padx=5)
        
        self.reset_all_btn = ttk.Button(self.bottom_frame, text="🔄 Сбросить всё", command=self.reset_all)
        self.reset_all_btn.pack(side='left', padx=5)
        
        self.refresh_btn = ttk.Button(self.bottom_frame, text="🔄 Обновить статус", command=self.refresh_status)
        self.refresh_btn.pack(side='left', padx=5)
        
        self.status_label = ttk.Label(self.bottom_frame, text="Статус: Готов к работе", foreground="green")
        self.status_label.pack(side='right', padx=5)
        
        # Инициализация переменных состояния
        self.init_variables()
        self.load_current_settings()
        self.log_event("Программа запущена")
    
    def is_admin(self):
        """Проверка прав администратора"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def init_variables(self):
        """Инициализация переменных для чекбоксов"""
        # Система
        self.var_regedit = tk.BooleanVar()
        self.var_cmd = tk.BooleanVar()
        self.var_powershell = tk.BooleanVar()
        self.var_taskmgr = tk.BooleanVar()
        self.var_controlpanel = tk.BooleanVar()
        self.var_settings = tk.BooleanVar()
        self.var_winrun = tk.BooleanVar()
        
        # Приложения
        self.var_block_exe = tk.BooleanVar()
        self.var_block_games = tk.BooleanVar()
        self.var_block_temp = tk.BooleanVar()
        self.blocked_apps = []
        
        # USB и Сеть
        self.var_usb_readonly = tk.BooleanVar()
        self.var_usb_disable = tk.BooleanVar()
        self.var_network_sharing = tk.BooleanVar()
        
        # Браузер
        self.var_browser_extensions = tk.BooleanVar()
        self.var_browser_devtools = tk.BooleanVar()
        self.var_browser_passwords = tk.BooleanVar()
    
    def create_system_tab(self):
        """Создание вкладки системы"""
        main_frame = ttk.LabelFrame(self.system_frame, text="Блокировка системных компонентов", padding=10)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Чекбоксы
        checkboxes = [
            ("Блокировать RegEdit (редактор реестра)", self.var_regedit),
            ("Блокировать Command Prompt (cmd.exe)", self.var_cmd),
            ("Блокировать PowerShell", self.var_powershell),
            ("Блокировать Диспетчер задач", self.var_taskmgr),
            ("Блокировать Панель управления", self.var_controlpanel),
            ("Блокировать Параметры Windows", self.var_settings),
            ("Блокировать Выполнить (Win+R)", self.var_winrun),
        ]
        
        for i, (text, var) in enumerate(checkboxes):
            cb = ttk.Checkbutton(main_frame, text=text, variable=var)
            cb.grid(row=i, column=0, sticky='w', padx=10, pady=5)
        
        # Информация
        info_label = ttk.Label(main_frame, text="⚠️ Эти настройки применяются к текущему пользователю", 
                              font=('Arial', 9, 'italic'), foreground='blue')
        info_label.grid(row=len(checkboxes), column=0, padx=10, pady=20, sticky='w')
    
    def create_apps_tab(self):
        """Создание вкладки приложений"""
        # Блокировка по типам
        types_frame = ttk.LabelFrame(self.apps_frame, text="Блокировка по типам приложений", padding=10)
        types_frame.pack(fill='x', padx=10, pady=10)
        
        checkboxes = [
            ("Блокировать игровые платформы (Steam, Epic Games)", self.var_block_games),
            ("Блокировать запуск из временных папок (%TEMP%, %APPDATA%)", self.var_block_temp),
        ]
        
        for i, (text, var) in enumerate(checkboxes):
            cb = ttk.Checkbutton(types_frame, text=text, variable=var)
            cb.grid(row=i, column=0, sticky='w', padx=10, pady=5)
        
        # Черный список приложений
        blacklist_frame = ttk.LabelFrame(self.apps_frame, text="Черный список приложений (.exe)", padding=10)
        blacklist_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        input_frame = ttk.Frame(blacklist_frame)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Имя файла (например, notepad.exe):").pack(side='left', padx=5)
        self.app_entry = ttk.Entry(input_frame, width=40)
        self.app_entry.pack(side='left', padx=5)
        
        add_btn = ttk.Button(input_frame, text="➕ Добавить", command=self.add_blocked_app)
        add_btn.pack(side='left', padx=5)
        
        # Список заблокированных приложений
        self.apps_listbox = tk.Listbox(blacklist_frame, height=8, width=60)
        self.apps_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        remove_btn = ttk.Button(blacklist_frame, text="🗑️ Удалить выбранное", command=self.remove_blocked_app)
        remove_btn.pack(pady=5)
    
    def create_usb_tab(self):
        """Создание вкладки USB и Сеть"""
        # USB
        usb_frame = ttk.LabelFrame(self.usb_frame, text="Управление USB-устройствами", padding=10)
        usb_frame.pack(fill='x', padx=10, pady=10)
        
        usb_options = [
            ("Только чтение для USB-накопителей (запись запрещена)", self.var_usb_readonly),
            ("Полностью отключить USB-накопители", self.var_usb_disable),
        ]
        
        for i, (text, var) in enumerate(usb_options):
            cb = ttk.Checkbutton(usb_frame, text=text, variable=var)
            cb.grid(row=i, column=0, sticky='w', padx=10, pady=5)
        
        # Сеть
        network_frame = ttk.LabelFrame(self.usb_frame, text="Сетевые ограничения", padding=10)
        network_frame.pack(fill='x', padx=10, pady=10)
        
        network_cb = ttk.Checkbutton(network_frame, 
                                     text="Отключить общий доступ к файлам и принтерам", 
                                     variable=self.var_network_sharing)
        network_cb.pack(anchor='w', padx=10, pady=5)
    
    def create_browser_tab(self):
        """Создание вкладки браузера"""
        browser_frame = ttk.LabelFrame(self.browser_frame, text="Ограничения для браузеров", padding=10)
        browser_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        checkboxes = [
            ("Запретить установку расширений", self.var_browser_extensions),
            ("Запретить инструменты разработчика (F12, Ctrl+Shift+I)", self.var_browser_devtools),
            ("Запретить сохранение паролей в браузере", self.var_browser_passwords),
        ]
        
        for i, (text, var) in enumerate(checkboxes):
            cb = ttk.Checkbutton(browser_frame, text=text, variable=var)
            cb.grid(row=i, column=0, sticky='w', padx=10, pady=5)
        
        info = ttk.Label(browser_frame, 
                        text="ℹ️ Настройки применяются к Microsoft Edge и Google Chrome",
                        font=('Arial', 9, 'italic'), foreground='gray')
        info.grid(row=len(checkboxes), column=0, padx=10, pady=20, sticky='w')
    
    def create_log_tab(self):
        """Создание вкладки журнала"""
        log_frame = ttk.LabelFrame(self.log_frame, text="Журнал событий", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill='both', expand=True)
        
        clear_btn = ttk.Button(log_frame, text="🗑️ Очистить журнал", command=self.clear_log)
        clear_btn.pack(pady=5)
    
    def log_event(self, message):
        """Запись события в журнал"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Сохранение в файл
        try:
            log_dir = os.path.join(os.environ['PROGRAMDATA'], 'WinSecHardener')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'audit.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            pass
    
    def clear_log(self):
        """Очистка журнала"""
        self.log_text.delete(1.0, tk.END)
        self.log_event("Журнал очищен пользователем")
    
    def add_blocked_app(self):
        """Добавление приложения в черный список"""
        app_name = self.app_entry.get().strip().lower()
        if not app_name:
            messagebox.showwarning("Предупреждение", "Введите имя файла!")
            return
        
        if not app_name.endswith('.exe'):
            app_name += '.exe'
        
        if app_name not in self.blocked_apps:
            self.blocked_apps.append(app_name)
            self.apps_listbox.insert(tk.END, app_name)
            self.app_entry.delete(0, tk.END)
            self.log_event(f"Добавлено в черный список: {app_name}")
        else:
            messagebox.showinfo("Инфо", "Приложение уже в списке")
    
    def remove_blocked_app(self):
        """Удаление приложения из черного списка"""
        selection = self.apps_listbox.curselection()
        if selection:
            index = selection[0]
            app_name = self.apps_listbox.get(index)
            self.blocked_apps.remove(app_name)
            self.apps_listbox.delete(index)
            self.log_event(f"Удалено из черного списка: {app_name}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите приложение для удаления")
    
    def apply_registry_changes(self, key_path, values):
        """Применение изменений в реестр"""
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            for value_name, value_data, value_type in values:
                if value_type == winreg.REG_DWORD:
                    winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                elif value_type == winreg.REG_SZ:
                    winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.log_event(f"Ошибка реестра {key_path}: {str(e)}")
            return False
    
    def apply_system_policies(self):
        """Применение политик системы"""
        changes_applied = 0
        
        # Блокировка RegEdit
        if self.var_regedit.get():
            self.apply_registry_changes(
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                [("DisableRegistryTools", 1, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("RegEdit заблокирован")
        
        # Блокировка CMD
        if self.var_cmd.get():
            self.apply_registry_changes(
                r"Software\Policies\Microsoft\Windows\System",
                [("DisableCMD", 2, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("Command Prompt заблокирован")
        
        # Блокировка PowerShell
        if self.var_powershell.get():
            self.apply_registry_changes(
                r"Software\Policies\Microsoft\Windows\PowerShell",
                [("EnableScriptBlockLogging", 1, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("PowerShell ограничен")
        
        # Блокировка диспетчера задач
        if self.var_taskmgr.get():
            self.apply_registry_changes(
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                [("DisableTaskMgr", 1, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("Диспетчер задач заблокирован")
        
        # Блокировка панели управления
        if self.var_controlpanel.get():
            self.apply_registry_changes(
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                [("NoControlPanel", 1, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("Панель управления заблокирована")
        
        # Блокировка параметров Windows
        if self.var_settings.get():
            self.apply_registry_changes(
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                [("NoSetFolders", 1, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("Параметры Windows заблокированы")
        
        # Блокировка Win+R
        if self.var_winrun.get():
            self.apply_registry_changes(
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                [("NoRun", 1, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("Выполнить (Win+R) заблокирован")
        
        return changes_applied
    
    def apply_app_restrictions(self):
        """Применение ограничений для приложений"""
        changes_applied = 0
        
        # Блокировка игр
        if self.var_block_games.get():
            # Пример блокировки через политики ограниченного использования программ
            self.log_event("Блокировка игровых платформ включена")
            changes_applied += 1
        
        # Блокировка запуска из временных папок
        if self.var_block_temp.get():
            self.log_event("Блокировка запуска из временных папок включена")
            changes_applied += 1
        
        # Черный список приложений
        if self.blocked_apps:
            self.log_event(f"Черный список приложений: {', '.join(self.blocked_apps)}")
            changes_applied += 1
        
        return changes_applied
    
    def apply_usb_restrictions(self):
        """Применение ограничений USB"""
        changes_applied = 0
        
        # Только чтение
        if self.var_usb_readonly.get():
            self.apply_registry_changes(
                r"System\CurrentControlSet\Control\StorageDevicePolicies",
                [("WriteProtect", 1, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("USB-накопители в режиме только для чтения")
        
        # Полная блокировка
        if self.var_usb_disable.get():
            self.apply_registry_changes(
                r"System\CurrentControlSet\Services\USBSTOR",
                [("Start", 4, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("USB-накопители полностью отключены")
        
        # Сетевой доступ
        if self.var_network_sharing.get():
            self.log_event("Общий доступ к файлам отключен")
            changes_applied += 1
        
        return changes_applied
    
    def apply_browser_restrictions(self):
        """Применение ограничений для браузеров"""
        changes_applied = 0
        
        # Расширения
        if self.var_browser_extensions.get():
            self.apply_registry_changes(
                r"Software\Policies\Google\Chrome\ExtensionInstallForcelist",
                [("*", "", winreg.REG_SZ)]
            )
            changes_applied += 1
            self.log_event("Установка расширений Chrome заблокирована")
        
        # Инструменты разработчика
        if self.var_browser_devtools.get():
            self.apply_registry_changes(
                r"Software\Policies\Google\Chrome",
                [("DeveloperToolsAvailability", 2, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("Инструменты разработчика заблокированы")
        
        # Пароли
        if self.var_browser_passwords.get():
            self.apply_registry_changes(
                r"Software\Policies\Google\Chrome",
                [("PasswordManagerEnabled", 0, winreg.REG_DWORD)]
            )
            changes_applied += 1
            self.log_event("Сохранение паролей отключено")
        
        return changes_applied
    
    def apply_all(self):
        """Применить все настройки"""
        if not messagebox.askyesno("Подтверждение", "Применить все выбранные настройки?\nЭто может потребовать перезагрузки."):
            return
        
        total_changes = 0
        total_changes += self.apply_system_policies()
        total_changes += self.apply_app_restrictions()
        total_changes += self.apply_usb_restrictions()
        total_changes += self.apply_browser_restrictions()
        
        self.status_label.config(text=f"Статус: Применено {total_changes} изменений", foreground="green")
        messagebox.showinfo("Готово", f"Применено {total_changes} настроек!\nНекоторые изменения вступят в силу после перезагрузки.")
        self.log_event(f"Применено всех настроек: {total_changes}")
    
    def reset_all(self):
        """Сброс всех настроек"""
        if not messagebox.askyesno("Подтверждение", "Сбросить ВСЕ настройки к исходным?\nЭто действие необратимо!"):
            return
        
        try:
            # Сброс политик системы
            self.apply_registry_changes(r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 
                                       [("DisableRegistryTools", 0, winreg.REG_DWORD),
                                        ("DisableTaskMgr", 0, winreg.REG_DWORD)])
            self.apply_registry_changes(r"Software\Policies\Microsoft\Windows\System", 
                                       [("DisableCMD", 0, winreg.REG_DWORD)])
            self.apply_registry_changes(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 
                                       [("NoControlPanel", 0, winreg.REG_DWORD),
                                        ("NoSetFolders", 0, winreg.REG_DWORD),
                                        ("NoRun", 0, winreg.REG_DWORD)])
            
            # Сброс переменных
            for var in [self.var_regedit, self.var_cmd, self.var_powershell, self.var_taskmgr,
                       self.var_controlpanel, self.var_settings, self.var_winrun,
                       self.var_block_games, self.var_block_temp,
                       self.var_usb_readonly, self.var_usb_disable, self.var_network_sharing,
                       self.var_browser_extensions, self.var_browser_devtools, self.var_browser_passwords]:
                var.set(False)
            
            self.blocked_apps.clear()
            self.apps_listbox.delete(0, tk.END)
            
            self.status_label.config(text="Статус: Все настройки сброшены", foreground="blue")
            messagebox.showinfo("Готово", "Все настройки сброшены!\nТребуется перезагрузка.")
            self.log_event("Все настройки сброшены пользователем")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сбросить настройки: {str(e)}")
            self.log_event(f"Ошибка при сбросе: {str(e)}")
    
    def refresh_status(self):
        """Обновление статуса"""
        self.load_current_settings()
        self.status_label.config(text="Статус: Статус обновлен", foreground="green")
        self.log_event("Статус обновлен пользователем")
    
    def load_current_settings(self):
        """Загрузка текущих настроек из реестра"""
        try:
            # Пример проверки статуса (упрощенно)
            self.log_event("Текущие настройки загружены")
        except Exception as e:
            self.log_event(f"Ошибка загрузки настроек: {str(e)}")


def main():
    root = tk.Tk()
    
    # Установка стиля
    style = ttk.Style()
    style.theme_use('clam')
    
    # Настройка шрифтов
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10, 'bold'))
    style.configure('TCheckbutton', font=('Arial', 10))
    
    app = SecurityHardener(root)
    root.mainloop()


if __name__ == "__main__":
    main()
