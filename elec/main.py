import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PIL import Image, ImageTk
import yaml  # For configuration management
import io
import logging
import os

# Configure logging
logging.basicConfig(
    filename='app.log',  # Log file name
    filemode='a',         # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG   # Log level
)

# Device Class
class Device:
    def __init__(self, name, power_w, count=1):
        self.name = name
        self.power_w = power_w
        self.count = count

    @property
    def power_kw(self):
        return self.power_w / 1000.0

# DeviceManager Class
class DeviceManager:
    def __init__(self):
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)
        logging.info(f"Added device: {device.name}, Power: {device.power_w}W, Count: {device.count}")

    def remove_device(self, device):
        if device in self.devices:
            self.devices.remove(device)
            logging.info(f"Removed device: {device.name}")

    def total_power_kw(self):
        total = sum(device.power_kw * device.count for device in self.devices)
        logging.debug(f"Total power (kW): {total}")
        return total

# CSVDataHandler Class
class CSVDataHandler:
    def __init__(self):
        self.data = None

    def load_csv(self, file_path, expected_days):
        try:
            df = pd.read_csv(file_path)
            if 'base_kw' not in df.columns:
                raise ValueError("CSV file must contain 'base_kw' column.")
            if len(df) != expected_days:
                raise ValueError(f"CSV file must have exactly {expected_days} rows.")
            self.data = df
            logging.info(f"CSV file '{file_path}' loaded successfully with {len(df)} rows.")
        except Exception as e:
            logging.error(f"Failed to load CSV file '{file_path}': {e}")
            raise e

# Calculator Class
class Calculator:
    def __init__(self, device_manager, csv_handler=None, config=None):
        self.device_manager = device_manager
        self.csv_handler = csv_handler
        self.config = config

    def calculate(self, hours_total, hours_home, hours_away):
        # Calculate total consumption
        if self.csv_handler and self.csv_handler.data is not None:
            daily_base_kw = self.csv_handler.data['base_kw'].values
            total_consumption = np.sum(daily_base_kw) * hours_total
            logging.debug(f"Total consumption from CSV: {total_consumption} kWh")
        else:
            # If no CSV, use manual total consumption input (handled externally)
            total_consumption = None
            logging.debug("No CSV data available. Using manual total consumption input.")

        # Determine tariff tier
        if total_consumption is not None and total_consumption > self.config['tariffs']['first_tier']['threshold']:
            rate = self.config['tariffs']['second_tier']['rate']
            tier = 'second'
            # Adjust hours_away proportionally (e.g., increase by 50% for second tier)
            proportional_hours_away = min(hours_away * 1.5, hours_total)
            logging.debug(f"Tier: {tier}, Rate: {rate}, Proportional Hours Away: {proportional_hours_away}")
        else:
            rate = self.config['tariffs']['first_tier']['rate']
            tier = 'first'
            proportional_hours_away = hours_away
            logging.debug(f"Tier: {tier}, Rate: {rate}, Proportional Hours Away: {proportional_hours_away}")

        # Get total power from devices
        total_power_kw = self.device_manager.total_power_kw()

        # Calculate consumption without EVi
        consumption_without_evi = total_power_kw * hours_total * self.config['defaults']['days_per_month']
        logging.debug(f"Consumption without EVi: {consumption_without_evi} kWh")

        # Calculate consumption with EVi
        consumption_with_evi = total_power_kw * (hours_total - proportional_hours_away) * self.config['defaults']['days_per_month']
        logging.debug(f"Consumption with EVi: {consumption_with_evi} kWh")

        # Calculate costs
        cost_without = consumption_without_evi * rate
        cost_with = consumption_with_evi * rate
        logging.debug(f"Cost without EVi: {cost_without} SAR, Cost with EVi: {cost_with} SAR")

        # Calculate savings
        savings = cost_without - cost_with
        logging.debug(f"Monthly Savings: {savings} SAR")

        # Calculate savings percentage
        savings_percentage = (savings / cost_without) * 100 if cost_without > 0 else 0
        logging.debug(f"Savings Percentage: {savings_percentage}%")

        return {
            'tier': tier,
            'rate': rate,
            'consumption_without_evi': consumption_without_evi,
            'consumption_with_evi': consumption_with_evi,
            'cost_without': cost_without,
            'cost_with': cost_with,
            'savings': savings,
            'savings_percentage': savings_percentage
        }

# Visualization Class
class Visualization:
    def __init__(self, plot_frame):
        self.plot_frame = plot_frame

    def plot_costs(self, days, cost_without, cost_with, savings_percentage, monthly_savings):
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=days, y=cost_without,
                name='Without EVi',
                marker_color='rgba(255,87,51,0.8)'
            )
        )
        fig.add_trace(
            go.Bar(
                x=days, y=cost_with,
                name='With EVi',
                marker_color='rgba(46,204,113,0.8)'
            )
        )

        fig.update_layout(
            barmode='group',
            title="Daily Cost Comparison (With vs Without EVi)",
            height=400, width=800,
            margin=dict(t=150),
            xaxis_title="Day",
            yaxis_title="Daily Cost (SAR)",
            legend=dict(x=0.7, y=1.1)
        )

        fig.add_annotation(
            x=0.01, y=1.25,
            xref='paper', yref='paper',
            text=(f"Monthly Savings Percentage: {savings_percentage:.2f}%\n"
                  f"Total Monthly Savings: {monthly_savings:.2f} SAR"),
            showarrow=False,
            font=dict(size=12, color="black", family="Arial")
        )

        img_bytes = fig.to_image(format="png")
        img_data = io.BytesIO(img_bytes)
        img = Image.open(img_data)
        tk_img = ImageTk.PhotoImage(img)

        # Clear previous plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        img_label = tk.Label(self.plot_frame, image=tk_img)
        img_label.image = tk_img  # Keep a reference to prevent garbage collection
        img_label.pack()

# ElectricityCalculatorApp Class
class ElectricityCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Electricity Cost Calculator")

        # Load configuration
        self.config = self.load_config()

        # Initialize managers
        self.device_manager = DeviceManager()
        self.csv_handler = CSVDataHandler()
        self.calculator = Calculator(self.device_manager, self.csv_handler, self.config)

        # Build UI
        self.build_ui()

    def load_config(self):
        try:
            with open('elec/config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            logging.info("Configuration loaded successfully.")
            print("Configuration loaded successfully:", config)  # Debugging statement
            return config
        except FileNotFoundError:
            logging.error("Configuration file 'elec/config.yaml' not found.")
            messagebox.showerror("Configuration Error", "Configuration file 'elec/config.yaml' not found.\nPlease ensure it exists in the application directory.")
            self.root.destroy()
            return None
        except yaml.YAMLError as e:
            logging.error(f"Error parsing 'elec/config.yaml': {e}")
            messagebox.showerror("Configuration Error", f"Error parsing 'elec/config.yaml':\n{e}")
            self.root.destroy()
            return None
        except Exception as e:
            logging.error(f"Unexpected error loading 'elec/config.yaml': {e}")
            messagebox.showerror("Configuration Error", f"An unexpected error occurred while loading 'elec/config.yaml':\n{e}")
            self.root.destroy()
            return None

    def build_ui(self):
        if self.config is None:
            return  # Exit if config failed to load

        # Basic Inputs Frame
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10, anchor='w')

        # Days per month
        tk.Label(self.input_frame, text="Days per month:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_days_per_month = tk.Entry(self.input_frame)
        self.entry_days_per_month.insert(0, str(self.config['defaults']['days_per_month']))
        self.entry_days_per_month.grid(row=0, column=1, padx=5, pady=5)

        # Load CSV Button
        self.load_csv_button = tk.Button(self.input_frame, text="Load CSV", command=self.load_csv)
        self.load_csv_button.grid(row=0, column=2, padx=5, pady=5)

        # Total consumption (disabled if CSV loaded)
        tk.Label(self.input_frame, text="Total consumption (kWh/month):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_total_consumption = tk.Entry(self.input_frame)
        self.entry_total_consumption.grid(row=1, column=1, padx=5, pady=5)

        # Total hours/day
        tk.Label(self.input_frame, text="Total hours/day:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_hours_total = tk.Entry(self.input_frame)
        self.entry_hours_total.insert(0, str(self.config['defaults']['hours_total']))
        self.entry_hours_total.grid(row=2, column=1, padx=5, pady=5)

        # Home hours/day
        tk.Label(self.input_frame, text="Home hours/day:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_hours_home = tk.Entry(self.input_frame)
        self.entry_hours_home.insert(0, str(self.config['defaults']['hours_home']))
        self.entry_hours_home.grid(row=3, column=1, padx=5, pady=5)

        # Total wasted hours (month)
        tk.Label(self.input_frame, text="Total wasted hours (month):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.entry_hours_away = tk.Entry(self.input_frame)
        self.entry_hours_away.insert(0, str(self.config['defaults']['hours_away']))
        self.entry_hours_away.grid(row=4, column=1, padx=5, pady=5)

        # Devices Frame
        self.devices_frame = tk.Frame(self.root)
        self.devices_frame.pack(fill='x', padx=10, pady=10)

        # AC Units Section
        self.ac_container = tk.LabelFrame(self.devices_frame, text="AC Units")
        self.ac_container.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.ac_manager_frame = tk.Frame(self.ac_container)
        self.ac_manager_frame.pack(fill='x', pady=5)
        self.ac_rows = []
        self.add_ac_button = tk.Button(self.ac_container, text="+ Add AC", command=self.add_ac_row)
        self.add_ac_button.pack(side='left', padx=5, pady=5)
        self.remove_ac_button = tk.Button(self.ac_container, text="- Remove AC", command=self.remove_ac_row)
        self.remove_ac_button.pack(side='left', padx=5, pady=5)
        self.add_ac_row()  # Add initial AC row

        # Bulbs Section
        self.bulb_container = tk.LabelFrame(self.devices_frame, text="Bulbs")
        self.bulb_container.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.bulb_manager_frame = tk.Frame(self.bulb_container)
        self.bulb_manager_frame.pack(fill='x', pady=5)
        self.bulb_rows = []
        self.add_bulb_button = tk.Button(self.bulb_container, text="+ Add Bulb", command=self.add_bulb_row)
        self.add_bulb_button.pack(side='left', padx=5, pady=5)
        self.remove_bulb_button = tk.Button(self.bulb_container, text="- Remove Bulb", command=self.remove_bulb_row)
        self.remove_bulb_button.pack(side='left', padx=5, pady=5)
        self.add_bulb_row()  # Add initial Bulb row

        # Calculate Button
        self.calculate_button = tk.Button(self.root, text="Calculate", command=self.calculate)
        self.calculate_button.pack(pady=10)

        # Results and Visualization Frame
        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Segment Label
        self.segment_label = tk.Label(self.results_frame, text="", justify=tk.LEFT, font=("Courier", 11))
        self.segment_label.pack(fill='x', padx=10, pady=5)

        # Results Text
        self.results_text = tk.Text(self.results_frame, height=10, width=80, state='disabled')
        self.results_text.pack(padx=10, pady=5)

        # Plot Frame
        self.plot_frame = tk.Frame(self.results_frame)
        self.plot_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Initialize Visualization
        self.visualization = Visualization(self.plot_frame)

    # Device row management
    def add_ac_row(self):
        row = tk.Frame(self.ac_manager_frame)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="AC Power (W):").pack(side='left', padx=5)
        power_entry = tk.Entry(row, width=10)
        power_entry.insert(0, str(self.config['defaults']['device_defaults']['AC']['power_w']))
        power_entry.pack(side='left', padx=5)
        tk.Label(row, text="Count:").pack(side='left', padx=5)
        count_entry = tk.Entry(row, width=5)
        count_entry.insert(0, str(self.config['defaults']['device_defaults']['AC']['count']))
        count_entry.pack(side='left', padx=5)
        self.ac_rows.append((power_entry, count_entry))
        logging.info("Added an AC row to the UI.")

    def remove_ac_row(self):
        if self.ac_rows:
            power_entry, count_entry = self.ac_rows.pop()
            power_entry.master.destroy()
            logging.info("Removed an AC row from the UI.")

    def add_bulb_row(self):
        row = tk.Frame(self.bulb_manager_frame)
        row.pack(fill='x', pady=2)
        tk.Label(row, text="Bulb Power (W):").pack(side='left', padx=5)
        power_entry = tk.Entry(row, width=10)
        power_entry.insert(0, str(self.config['defaults']['device_defaults']['Bulb']['power_w']))
        power_entry.pack(side='left', padx=5)
        tk.Label(row, text="Count:").pack(side='left', padx=5)
        count_entry = tk.Entry(row, width=5)
        count_entry.insert(0, str(self.config['defaults']['device_defaults']['Bulb']['count']))
        count_entry.pack(side='left', padx=5)
        self.bulb_rows.append((power_entry, count_entry))
        logging.info("Added a Bulb row to the UI.")

    def remove_bulb_row(self):
        if self.bulb_rows:
            power_entry, count_entry = self.bulb_rows.pop()
            power_entry.master.destroy()
            logging.info("Removed a Bulb row from the UI.")

    # CSV loading
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if file_path:
            try:
                days = int(self.entry_days_per_month.get())
                self.csv_handler.load_csv(file_path, days)
                messagebox.showinfo("Success", "CSV file loaded successfully.")
                # Disable total consumption entry
                self.entry_total_consumption.config(state='disabled')
                logging.info(f"CSV file '{file_path}' loaded and total consumption entry disabled.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file.\n{e}")
                logging.error(f"Failed to load CSV file '{file_path}': {e}")

    # Calculation and Plotting
    def calculate(self):
        # Gather inputs
        try:
            days = int(self.entry_days_per_month.get())
            hours_total = float(self.entry_hours_total.get())
            hours_home = float(self.entry_hours_home.get())
            hours_away = float(self.entry_hours_away.get())
            logging.debug(f"Input - Days: {days}, Hours Total: {hours_total}, Hours Home: {hours_home}, Hours Away: {hours_away}")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for all inputs.")
            logging.warning("Invalid input: Non-numeric values entered.")
            return

        if hours_home > hours_total:
            messagebox.showerror("Input Error", "Home hours cannot exceed total hours.")
            logging.warning("Invalid input: Home hours exceed total hours.")
            return

        # Update device manager
        self.device_manager.devices.clear()
        logging.debug("Cleared existing devices from DeviceManager.")

        for power_entry, count_entry in self.ac_rows:
            try:
                power = float(power_entry.get())
                count = int(count_entry.get())
                if power < 0 or count < 0:
                    raise ValueError
                self.device_manager.add_device(Device("AC", power, count))
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid positive numbers for AC power and count.")
                logging.warning("Invalid input: Non-positive numbers entered for AC.")
                return

        for power_entry, count_entry in self.bulb_rows:
            try:
                power = float(power_entry.get())
                count = int(count_entry.get())
                if power < 0 or count < 0:
                    raise ValueError
                self.device_manager.add_device(Device("Bulb", power, count))
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid positive numbers for Bulb power and count.")
                logging.warning("Invalid input: Non-positive numbers entered for Bulb.")
                return

        # Perform calculation
        try:
            results = self.calculator.calculate(hours_total, hours_home, hours_away)
            logging.info("Calculation performed successfully.")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred during calculation.\n{e}")
            logging.error(f"Calculation error: {e}")
            return

        # Display results
        self.display_results(results, days)

        # Plot results
        days_list = list(range(1, days + 1))
        # Assuming equal distribution of consumption across days
        daily_consumption_without = results['consumption_without_evi'] / days
        daily_consumption_with = results['consumption_with_evi'] / days
        daily_cost_without = results['cost_without'] / days
        daily_cost_with = results['cost_with'] / days

        self.visualization.plot_costs(
            days_list,
            [daily_cost_without] * days,
            [daily_cost_with] * days,
            results['savings_percentage'],
            results['savings']
        )
        logging.info("Plot generated successfully.")

    def display_results(self, results, days):
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)

        # Segment Information
        tier_text = f"Tier: {'First' if results['tier'] == 'first' else 'Second'}\n"
        tier_text += f"Rate: {results['rate']} SAR/kWh"
        self.segment_label.config(
            text=tier_text,
            bg="green" if results['tier'] == 'first' else "red",
            fg="white"
        )

        # Detailed Results
        table_header = "Day | kWh (Without EVi) | Cost (Without EVi) | kWh (With EVi) | Cost (With EVi)\n"
        table_divider = "-" * len(table_header) + "\n"
        self.results_text.insert(tk.END, table_header)
        self.results_text.insert(tk.END, table_divider)

        # Populate table with daily data
        daily_consumption_without = results['consumption_without_evi'] / days
        daily_cost_without = results['cost_without'] / days
        daily_consumption_with = results['consumption_with_evi'] / days
        daily_cost_with = results['cost_with'] / days

        for day in range(days):
            self.results_text.insert(tk.END, f"{day+1:>3} | {daily_consumption_without:>17.2f} | {daily_cost_without:>18.2f} | {daily_consumption_with:>15.2f} | {daily_cost_with:>14.2f}\n")

        self.results_text.insert(tk.END, "\n" + table_divider)
        self.results_text.insert(tk.END, f"Monthly Consumption Without EVi: {results['consumption_without_evi']:.2f} kWh\n")
        self.results_text.insert(tk.END, f"Monthly Cost Without EVi: {results['cost_without']:.2f} SAR\n")
        self.results_text.insert(tk.END, f"Monthly Consumption With EVi: {results['consumption_with_evi']:.2f} kWh\n")
        self.results_text.insert(tk.END, f"Monthly Cost With EVi: {results['cost_with']:.2f} SAR\n")
        self.results_text.insert(tk.END, f"Monthly Savings: {results['savings']:.2f} SAR\n")
        self.results_text.insert(tk.END, f"Savings Percentage: {results['savings_percentage']:.2f}%\n")

        self.results_text.config(state='disabled')
        logging.debug("Results displayed in the GUI.")

# Main Function
def main():
    root = tk.Tk()
    app = ElectricityCalculatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
