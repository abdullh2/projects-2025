import tkinter as tk
from tkinter import filedialog, messagebox
from main import PrescriptionAnalysisSystem

def browse_and_process():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png")])
    if not file_path:
        return

    try:
        system = PrescriptionAnalysisSystem()
        results = system.process_prescription(file_path)

        text_output = f"Extracted Text:\n{results['ocr']['text']}\n\n"
        text_output += f"Confidence: {results['ocr']['confidence']}%\n\n"
        text_output += f"Recognized Medications: {', '.join(results['ner'])}\n\n"
        text_output += "Drug Interactions:\n"

        for med, interaction in results['interactions'].items():
            text_output += f"\n{med}:\n"
            if 'error' in interaction:
                text_output += f"- Error: {interaction['error']}\n"
            else:
                text_output += f"- Total Reports: {interaction['total_reports']}\n"
                text_output += "- Top Reactions:\n"
                for reaction, count in interaction.get('reactions', {}).items():
                    text_output += f"  • {reaction}: {count} reports\n"

        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, text_output)

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Prescription Text Analyzer")
root.geometry("800x600")

tk.Button(root, text="Browse Prescription Image", command=browse_and_process).pack(pady=10)

output_text = tk.Text(root, wrap=tk.WORD)
output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

root.mainloop()
