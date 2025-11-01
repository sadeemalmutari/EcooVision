import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import io
import numpy as np
import plotly.graph_objects as go
from PIL import Image, ImageTk
import pandas as pd
import csv

# متغيرات لتخزين بيانات CSV والنتائج
csv_data = None
results_data = None  # لتخزين نتائج الحسابات
latest_fig = None  # لتخزين الرسم البياني الأخير

def add_ac_row():
    frame = tk.Frame(ac_frame, bg=ac_frame_bg)
    frame.pack(fill='x', pady=2)
    tk.Label(frame, text=f"AC {len(ac_rows)+1} Power (W):", bg=ac_frame_bg).pack(side='left', padx=5)
    ac_power_entry = tk.Entry(frame)
    ac_power_entry.insert(0, "1612")
    ac_power_entry.pack(side='left', padx=5)

    tk.Label(frame, text="Count:", bg=ac_frame_bg).pack(side='left', padx=5)
    ac_count_entry = tk.Entry(frame)
    ac_count_entry.insert(0, "1")
    ac_count_entry.pack(side='left', padx=5)

    ac_rows.append((frame, ac_power_entry, ac_count_entry))

def remove_ac_row():
    if ac_rows:
        row = ac_rows.pop()
        row_frame = row[0]
        row_frame.destroy()

def add_bulb_row():
    frame = tk.Frame(bulb_frame, bg=bulb_frame_bg)
    frame.pack(fill='x', pady=2)
    tk.Label(frame, text=f"Bulb {len(bulb_rows)+1} Power (W):", bg=bulb_frame_bg).pack(side='left', padx=5)
    bulb_power_entry = tk.Entry(frame)
    bulb_power_entry.insert(0, "16")
    bulb_power_entry.pack(side='left', padx=5)

    tk.Label(frame, text="Count:", bg=bulb_frame_bg).pack(side='left', padx=5)
    bulb_count_entry = tk.Entry(frame)
    bulb_count_entry.insert(0, "1")
    bulb_count_entry.pack(side='left', padx=5)

    bulb_rows.append((frame, bulb_power_entry, bulb_count_entry))

def remove_bulb_row():
    if bulb_rows:
        row = bulb_rows.pop()
        row_frame = row[0]
        row_frame.destroy()

# دالة لتحميل ملف CSV
def load_csv():
    global csv_data
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    if file_path:
        try:
            df = pd.read_csv(file_path)
            # التحقق من وجود العمود المطلوب
            if 'base_kw' not in df.columns:
                messagebox.showerror("Error", "CSV file must contain 'base_kw' column representing daily consumption in kWh.")
                return
            if len(df) != int(entry_days_per_month.get()):
                messagebox.showerror("Error", f"CSV file must have exactly {entry_days_per_month.get()} rows.")
                return
            csv_data = df
            messagebox.showinfo("Success", "CSV file loaded successfully.")
            # تعطيل إدخال "Total consumption (kWh/month)"
            entry_total_consumption.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file.\n{e}")

def calculate_and_plot():
    global csv_data, results_data, latest_fig
    try:
        days_per_month = int(entry_days_per_month.get())
        hours_total = float(entry_hours_total.get())
        hours_home = float(entry_hours_home.get())
        total_hours_away = float(entry_hours_away_hader.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for the parameters.")
        return

    if total_hours_away < 0 or days_per_month <= 0 or hours_total <= 0 or hours_home < 0:
        messagebox.showerror("Input Error", "Please enter positive values where appropriate.")
        return

    if hours_home > hours_total:
        messagebox.showerror("Input Error", "Home hours cannot exceed total hours.")
        return

    # حساب الاستهلاك الأساسي من الأجهزة
    total_kw_ac = 0.0
    for (frame, p_entry, c_entry) in ac_rows:
        try:
            power = float(p_entry.get())
            count = int(c_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input in AC rows.")
            return
        if power < 0 or count < 0:
            messagebox.showerror("Input Error", "AC power/count must be positive.")
            return
        kw = power / 1000.0
        total_kw_ac += kw * count

    total_kw_bulb = 0.0
    for (frame, p_entry, c_entry) in bulb_rows:
        try:
            power = float(p_entry.get())
            count = int(c_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input in Bulb rows.")
            return
        if power < 0 or count < 0:
            messagebox.showerror("Input Error", "Bulb power/count must be positive.")
            return
        kw = power / 1000.0
        total_kw_bulb += kw * count

    # حساب الاستهلاك الأساسي من الأجهزة
    devices_kwh = (total_kw_ac + total_kw_bulb) * hours_total  # kWh شهريًا

    # خيار احتساب الاستهلاك من الأجهزة
    include_devices = var_include_devices.get()

    # إعادة تعيين الاستهلاك اليومي بدون EVi بناءً على CSV أو المدخلات
    if csv_data is not None:
        # حساب الاستهلاك الإجمالي من CSV base_kw
        daily_kwh_base = csv_data['base_kw'].values.copy()  # kWh يوميًا بدون الأجهزة
        total_consumption_without = np.sum(daily_kwh_base)
    else:
        try:
            daily_kwh_base = np.full(days_per_month, float(entry_total_consumption.get()) / days_per_month)
            total_consumption_without = float(entry_total_consumption.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid value for Total consumption.")
            return

    if include_devices:
        # توزيع استهلاك الأجهزة على الأيام
        daily_kwh_without = daily_kwh_base + (devices_kwh / days_per_month)
        total_consumption_without += devices_kwh
    else:
        daily_kwh_without = daily_kwh_base.copy()

    # تحديد السعر بناءً على الاستهلاك الإجمالي بدون EVi
    if total_consumption_without <= 6000:
        # الشريحة الأولى
        cost_per_kwh_without = 0.18  # SAR/kWh
        segment_msg = f"First Tier (1 to 6000 kWh/month)\nRate: {cost_per_kwh_without} SAR/kWh"
        segment_label.config(text=segment_msg, bg="green", fg="white")
    else:
        # الشريحة الثانية
        cost_per_kwh_without = 0.30  # SAR/kWh
        segment_msg = f"Second Tier (> 6000 kWh/month)\nRate: {cost_per_kwh_without} SAR/kWh"
        segment_label.config(text=segment_msg, bg="red", fg="white")

    # توزيع ساعات التواجد خارج المنزل بشكل متساوٍ عبر الأيام
    day_hours_away = np.full(days_per_month, total_hours_away / days_per_month)

    # إضافة تباين ±5% على الاستهلاك اليومي بدون EVi
    rng = np.random.default_rng()
    variation_factors = rng.uniform(0.95, 1.05, days_per_month)
    daily_kwh_without = daily_kwh_without * variation_factors

    # حساب الاستهلاك مع EVi
    daily_kwh_with = daily_kwh_without * (hours_total - day_hours_away) / hours_total  # kWh يوميًا مع EVi

    # حساب الاستهلاك الإجمالي مع EVi
    total_consumption_with = np.sum(daily_kwh_with)

    # تحديد السعر بناءً على الاستهلاك الإجمالي مع EVi
    if total_consumption_with <= 6000:
        # الشريحة الأولى
        cost_per_kwh_with = 0.18  # SAR/kWh
    else:
        # الشريحة الثانية
        cost_per_kwh_with = 0.30  # SAR/kWh

    # حساب التكاليف
    daily_cost_without = daily_kwh_without * cost_per_kwh_without
    daily_cost_with = daily_kwh_with * cost_per_kwh_with

    # المجاميع الشهرية
    monthly_cost_without = np.sum(daily_cost_without)
    monthly_cost_with = np.sum(daily_cost_with)
    monthly_savings = monthly_cost_without - monthly_cost_with

    monthly_kwh_without = np.sum(daily_kwh_without)
    monthly_kwh_with = np.sum(daily_kwh_with)

    if monthly_cost_without > 0:
        savings_percentage = (monthly_savings / monthly_cost_without) * 100
    else:
        savings_percentage = 0

    # تخزين النتائج
    results_data = {
        'Day': np.arange(1, days_per_month + 1),
        'kWh(W/O)': daily_kwh_without,
        'Cost(W/O) SAR': daily_cost_without,
        'kWh(W)': daily_kwh_with,
        'Cost(W) SAR': daily_cost_with
    }

    # عرض النتائج في tkinter.Text
    results_text.config(state='normal')
    results_text.delete('1.0', tk.END)
    results_text.insert(tk.END, "Day | kWh(W/O) | Cost(W/O) SAR | kWh(W)  | Cost(W) SAR\n")
    results_text.insert(tk.END, "-"*70 + "\n")
    for i in range(days_per_month):
        results_text.insert(tk.END, f"{i+1:>2d}  | {daily_kwh_without[i]:>7.2f} | {daily_cost_without[i]:>13.2f} | {daily_kwh_with[i]:>7.2f} | {daily_cost_with[i]:>12.2f}\n")
    results_text.insert(tk.END, "\n" + "-"*70 + "\n")
    results_text.insert(tk.END, f"Monthly W/O EVi: kWh={monthly_kwh_without:.2f}, Cost={monthly_cost_without:.2f} SAR\n")
    results_text.insert(tk.END, f"Monthly With EVi: kWh={monthly_kwh_with:.2f}, Cost={monthly_cost_with:.2f} SAR\n")
    results_text.insert(tk.END, f"Monthly Savings: {monthly_savings:.2f} SAR\n")
    results_text.insert(tk.END, f"Savings Percentage: {savings_percentage:.2f}%\n")
    results_text.config(state='disabled')

    # حفظ النتائج في DataFrame
    df_results = pd.DataFrame(results_data)
    summary = {
        'Monthly kWh W/O EVi': [monthly_kwh_without],
        'Monthly Cost W/O EVi (SAR)': [monthly_cost_without],
        'Monthly kWh With EVi': [monthly_kwh_with],
        'Monthly Cost With EVi (SAR)': [monthly_cost_with],
        'Monthly Savings (SAR)': [monthly_savings],
        'Savings Percentage (%)': [savings_percentage]
    }
    df_summary = pd.DataFrame(summary)

    # دمج الجداول
    full_results = pd.concat([df_results, df_summary], axis=1)

    # رسم الرسم البياني باستخدام plotly
    for widget in plot_frame.winfo_children():
        widget.destroy()

    fig = go.Figure()
    # إضافة "With EVi" أولاً لضمان أن "Without EVi" تكون على اليمين
    fig.add_trace(
        go.Bar(
            x=results_data['Day'], y=results_data['Cost(W) SAR'],
            name='With EVi',
            marker_color='rgba(46,204,113,0.8)'
        )
    )
    fig.add_trace(
        go.Bar(
            x=results_data['Day'], y=results_data['Cost(W/O) SAR'],
            name='Without EVi',
            marker_color='rgba(255,87,51,0.8)'
        )
    )

    fig.update_layout(
        barmode='group',
        title="Daily Cost Comparison (With/Without EVi)",
        height=400, width=800,
        margin=dict(t=150),
        xaxis_title="Day",
        yaxis_title="Daily Cost (SAR)",
        legend=dict(
            x=1.0,  # موقع x خارج الرسم البياني على اليمين
            y=1.0,  # موقع y في أعلى الرسم البياني
            traceorder='normal'
        )
    )

    fig.add_annotation(
        x=0.5, y=1.15,
        xref='paper', yref='paper',
        text=(f"Monthly Savings Percentage: {savings_percentage:.2f}%\n"
              f"Total monthly kWh W/O EVi: {monthly_kwh_without:.2f}\n"
              f"Total monthly kWh With EVi: {monthly_kwh_with:.2f}"),
        showarrow=False,
        font=dict(size=12, color="black", family="Arial"),
        align="center"
    )

    # تخزين الرسم البياني الأخير
    latest_fig = fig

    # إنشاء صورة الرسم البياني بحجم عادي للعرض في Tkinter
    img_bytes = fig.to_image(format="png", scale=1)  # scale=1 للحفاظ على الحجم المعروض
    img_data = io.BytesIO(img_bytes)
    img = Image.open(img_data)
    tk_img = ImageTk.PhotoImage(img)

    img_label = tk.Label(plot_frame, image=tk_img)
    img_label.image = tk_img
    img_label.pack()

def save_plot():
    global latest_fig
    if latest_fig is None:
        messagebox.showerror("Error", "No plot available to save. Please perform calculations first.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")],
        title="Save Plot As"
    )
    if file_path:
        try:
            # زيادة scale لزيادة الدقة
            img_bytes = latest_fig.to_image(format="png", scale=4)  # scale=4 لزيادة الدقة
            with open(file_path, 'wb') as f:
                f.write(img_bytes)
            messagebox.showinfo("Success", f"Plot saved successfully at {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot.\n{e}")

def save_table_image():
    if results_data is None:
        messagebox.showerror("Error", "No data table available to save. Please perform calculations first.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")],
        title="Save Table As Image"
    )
    if file_path:
        try:
            # إنشاء DataFrame
            df_table = pd.DataFrame(results_data)

            # إنشاء رسم بياني جديد لجدول البيانات باستخدام plotly
            fig_table = go.Figure(data=[go.Table(
                header=dict(values=list(df_table.columns),
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df_table[col] for col in df_table.columns],
                           fill_color='lavender',
                           align='left'))
            ])

            fig_table.update_layout(margin=dict(l=10, r=10, t=10, b=10))

            # حفظ جدول البيانات كصورة عالية الدقة
            img_bytes = fig_table.to_image(format="png", scale=4)  # scale=4 لزيادة الدقة
            with open(file_path, 'wb') as f:
                f.write(img_bytes)
            messagebox.showinfo("Success", f"Data table saved successfully at {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data table.\n{e}")

def save_results():
    if results_data is None:
        messagebox.showerror("Error", "No results to save. Please perform calculations first.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")],
        title="Save Results As"
    )
    if file_path:
        try:
            df = pd.DataFrame(results_data)
            # إضافة ملخص النتائج
            monthly_summary = {
                'Monthly kWh W/O EVi': [np.sum(results_data['kWh(W/O)'])],
                'Monthly Cost W/O EVi (SAR)': [np.sum(results_data['Cost(W/O) SAR'])],
                'Monthly kWh With EVi': [np.sum(results_data['kWh(W)'])],
                'Monthly Cost With EVi (SAR)': [np.sum(results_data['Cost(W) SAR'])],
                'Monthly Savings (SAR)': [np.sum(results_data['Cost(W/O) SAR']) - np.sum(results_data['Cost(W) SAR'])],
                'Savings Percentage (%)': [(np.sum(results_data['Cost(W/O) SAR']) - np.sum(results_data['Cost(W) SAR'])) / np.sum(results_data['Cost(W/O) SAR']) * 100 if np.sum(results_data['Cost(W/O) SAR']) > 0 else 0]
            }
            df_summary = pd.DataFrame(summary := monthly_summary)  # Defining summary in one step

            # حفظ في CSV أو Excel بناءً على الامتداد
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
                with open(file_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([])
                    writer.writerow(['Monthly Summary'])
                df_summary.to_csv(file_path, mode='a', header=True, index=False)
            elif file_path.endswith('.xlsx'):
                with pd.ExcelWriter(file_path) as writer:
                    df.to_excel(writer, sheet_name='Daily Results', index=False)
                    df_summary.to_excel(writer, sheet_name='Monthly Summary', index=False)
            messagebox.showinfo("Success", f"Results saved successfully at {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results.\n{e}")

# واجهة المستخدم
root = tk.Tk()
root.title("Electricity Cost Calculation")

ac_frame_bg = "#e6f7ff"
bulb_frame_bg = "#fff2e6"

# إطار النص العلوي الأيمن
header_frame = tk.Frame(root)
header_frame.pack(side='top', fill='x', padx=10, pady=5)

# إطار فرعي لاحتواء النص في الجانب الأيسر (يمكن تركه فارغًا أو استخدامه لمكونات أخرى)
left_header = tk.Frame(header_frame)
left_header.pack(side='left', fill='x', expand=True)

# إطار فرعي لاحتواء النص في الجانب الأيمن
right_header = tk.Frame(header_frame)
right_header.pack(side='right', anchor='ne')

# إضافة النص في الجانب الأيمن
header_text = (
    "These readings are based on a monthly consumption value with some devices such as AC and bulbs "
    "left on for one hour daily. The added value from the program is shown through the statistics "
    "presented in this window."
)
header_label = tk.Label(right_header, text=header_text, justify='right', wraplength=400, font=("Arial", 10))
header_label.pack()

# إطار المدخلات الأساسية
input_frame = tk.Frame(root)
input_frame.pack(pady=10, anchor='w', padx=10)

tk.Label(input_frame, text="Days per month:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_days_per_month = tk.Entry(input_frame)
entry_days_per_month.insert(0, "30")
entry_days_per_month.grid(row=0, column=1, padx=5, pady=5)

# زر تحميل CSV
load_csv_button = tk.Button(input_frame, text="Load CSV", command=load_csv)
load_csv_button.grid(row=0, column=2, padx=5, pady=5)

tk.Label(input_frame, text="Total consumption (kWh/month):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_total_consumption = tk.Entry(input_frame)  # يترك فارغ
entry_total_consumption.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Total hours/day:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_hours_total = tk.Entry(input_frame)
entry_hours_total.insert(0, "24")
entry_hours_total.grid(row=2, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Home hours/day:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry_hours_home = tk.Entry(input_frame)
entry_hours_home.insert(0, "22")
entry_hours_home.grid(row=3, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Total wasted hours (month):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry_hours_away_hader = tk.Entry(input_frame)
entry_hours_away_hader.insert(0, "30")
entry_hours_away_hader.grid(row=4, column=1, padx=5, pady=5)

# إضافة خيار احتساب استهلاك الأجهزة
var_include_devices = tk.BooleanVar(value=True)
include_devices_checkbox = tk.Checkbutton(
    input_frame,
    text="Include AC and Bulb Consumption",
    variable=var_include_devices,
    bg=root.cget('bg')
)
include_devices_checkbox.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")

# إطار الأجهزة
devices_frame = tk.Frame(root)
devices_frame.pack(fill='x', padx=10, pady=10)

# قسم المكيفات
ac_container = tk.LabelFrame(devices_frame, text="AC Units", bg=ac_frame_bg)
ac_container.pack(side='left', fill='both', expand=True, padx=10, pady=10)
ac_frame = tk.Frame(ac_container, bg=ac_frame_bg)  # تم تغيير الاسم من ac_frame_inner إلى ac_frame
ac_frame.pack(fill='x', pady=5)
ac_rows = []
ac_btn_frame = tk.Frame(ac_container, bg=ac_frame_bg)
ac_btn_frame.pack(fill='x', pady=5, padx=5)
add_ac_button = tk.Button(ac_btn_frame, text="+ Add AC", command=add_ac_row)
add_ac_button.pack(side='left', padx=5)
remove_ac_button = tk.Button(ac_btn_frame, text="- Remove AC", command=remove_ac_row)
remove_ac_button.pack(side='left', padx=5)
add_ac_row()

# قسم المصابيح
bulb_container = tk.LabelFrame(devices_frame, text="Bulbs", bg=bulb_frame_bg)
bulb_container.pack(side='left', fill='both', expand=True, padx=10, pady=10)
bulb_frame = tk.Frame(bulb_container, bg=bulb_frame_bg)  # تم تغيير الاسم من bulb_frame_inner إلى bulb_frame
bulb_frame.pack(fill='x', pady=5)
bulb_rows = []
bulb_btn_frame = tk.Frame(bulb_container, bg=bulb_frame_bg)
bulb_btn_frame.pack(fill='x', pady=5, padx=5)
add_bulb_button = tk.Button(bulb_btn_frame, text="+ Add Bulb", command=add_bulb_row)
add_bulb_button.pack(side='left', padx=5)
remove_bulb_button = tk.Button(bulb_btn_frame, text="- Remove Bulb", command=remove_bulb_row)
remove_bulb_button.pack(side='left', padx=5)
add_bulb_row()

# أزرار الحساب والحفظ
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10, anchor='w', padx=10)
btn = tk.Button(btn_frame, text="Calculate", command=calculate_and_plot)
btn.pack(side='left', padx=5)
save_results_btn = tk.Button(btn_frame, text="Save Results", command=save_results)
save_results_btn.pack(side='left', padx=5)
save_plot_btn = tk.Button(btn_frame, text="Save Plot", command=save_plot)
save_plot_btn.pack(side='left', padx=5)
save_table_btn = tk.Button(btn_frame, text="Save Table as Image", command=save_table_image)
save_table_btn.pack(side='left', padx=5)

# إطار النتائج والرسم البياني
horizontal_frame = tk.Frame(root)
horizontal_frame.pack(fill='both', expand=True, padx=10, pady=10)

segment_label = tk.Label(horizontal_frame, text="", justify='left', font=("Courier", 11))
segment_label.pack(fill='x', padx=10, pady=5)

results_frame = tk.Frame(horizontal_frame)
results_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

# استخدام tkinter.Text لعرض النتائج مع إضافة أشرطة تمرير
results_text = tk.Text(results_frame, wrap='none', font=("Courier", 9))
results_text.pack(fill='both', expand=True)

# إضافة أشرطة تمرير عمودية وأفقية
scroll_y = tk.Scrollbar(results_frame, command=results_text.yview)
scroll_y.pack(side='right', fill='y')
scroll_x = tk.Scrollbar(results_frame, command=results_text.xview, orient='horizontal')
scroll_x.pack(side='bottom', fill='x')
results_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

plot_frame = tk.Frame(horizontal_frame)
plot_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

root.mainloop()
