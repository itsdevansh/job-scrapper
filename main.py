import tkinter as tk
from tkinter import ttk, messagebox
from jobspy import scrape_jobs
import csv
from datetime import datetime

class JobSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Search Tool")
        self.root.geometry("600x700")
        
        # Force window to front on macOS
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Job Sites
        ttk.Label(main_frame, text="Job Sites:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sites = ["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"]
        self.site_vars = {}
        site_frame = ttk.Frame(main_frame)
        site_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        for i, site in enumerate(self.sites):
            self.site_vars[site] = tk.BooleanVar(value=True)
            ttk.Checkbutton(site_frame, text=site, variable=self.site_vars[site]).grid(row=0, column=i, padx=5)
        
        # Search Term
        ttk.Label(main_frame, text="Search Term:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.search_term = ttk.Entry(main_frame, width=40)
        self.search_term.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Location
        ttk.Label(main_frame, text="Location:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.location = ttk.Entry(main_frame, width=40)
        self.location.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Job Type
        ttk.Label(main_frame, text="Job Type:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.job_type = ttk.Combobox(main_frame, values=["", "fulltime", "parttime", "internship", "contract"])
        self.job_type.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Results Wanted
        ttk.Label(main_frame, text="Results per site:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.results_wanted = ttk.Entry(main_frame, width=10)
        self.results_wanted.insert(0, "20")
        self.results_wanted.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Remote Option
        self.is_remote = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Remote Only", variable=self.is_remote).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Country Selection (for Indeed)
        ttk.Label(main_frame, text="Country (Indeed/Glassdoor):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.country = ttk.Combobox(main_frame, values=["USA", "UK", "Canada", "Australia", "Germany", "France"])
        self.country.set("USA")
        self.country.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # Progress Text
        self.progress_text = tk.Text(main_frame, height=10, width=60)
        self.progress_text.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Search Button
        ttk.Button(main_frame, text="Search Jobs", command=self.search_jobs).grid(row=9, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
    def log_progress(self, message):
        self.progress_text.insert(tk.END, f"{message}\n")
        self.progress_text.see(tk.END)
        self.root.update()
        
    def search_jobs(self):
        try:
            # [Previous validation code remains the same...]
            
            self.log_progress("Searching for jobs...")
            jobs = scrape_jobs(**params)
            
            if len(jobs) == 0:
                self.log_progress("No jobs found matching your criteria.")
                return
            
            # Drop unwanted columns
            columns_to_drop = [
                'company_industry',
                'job_url_direct',
                'job_type',
                'is_remote',
                'job_level',
                'job_function',
                'emails',
                'company_url',
                'company_logo',
                'company_url_direct',
                'company_addresses',
                'company_num_employees',
                'company_revenue',
                'company_description'
            ]
            
            # Drop columns if they exist in the DataFrame
            jobs = jobs.drop(columns=[col for col in columns_to_drop if col in jobs.columns])
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_search_results_{timestamp}.xlsx"
            
            # Export to Excel
            jobs.to_excel(filename, index=False)
            self.log_progress(f"Found {len(jobs)} jobs")
            self.log_progress(f"Results exported to: {filename}")
            
            # Show success message
            messagebox.showinfo("Success", f"Search completed!\nFound {len(jobs)} jobs\nResults saved to {filename}")
            
        except Exception as e:
            self.log_progress(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    
    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 600
    window_height = 700
    x = (screen_width/2) - (window_width/2)
    y = (screen_height/2) - (window_height/2)
    root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')
    
    # Create the application
    app = JobSearchApp(root)
    
    # Start the event loop
    root.mainloop()

if __name__ == "__main__":
    print("Starting application...")
    main()
    print("Application closed")