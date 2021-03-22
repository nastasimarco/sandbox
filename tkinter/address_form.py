import tkinter as tk

window = tk.Tk()
window.title("Address Entry Form")

frm_entries = tk.Frame(master=window, relief=tk.SUNKEN, borderwidth=3)
frm_entries.pack()

lbl_first_name = tk.Label(master=frm_entries, text="First Name:")
ent_first_name = tk.Entry(master=frm_entries, width=60)
lbl_last_name = tk.Label(master=frm_entries, text="Last Name:")
ent_last_name = tk.Entry(master=frm_entries)
ent_address_1 = tk.Entry(master=frm_entries)
lbl_address_1 = tk.Label(master=frm_entries, text="Address Line 1:")
ent_address_2 = tk.Entry(master=frm_entries)
lbl_address_2 = tk.Label(master=frm_entries, text="Address Line 2:")
ent_city = tk.Entry(master=frm_entries)
lbl_city = tk.Label(master=frm_entries, text="City:")
ent_state_province = tk.Entry(master=frm_entries)
lbl_state_province = tk.Label(master=frm_entries, text="State/Province:")
ent_postal_code = tk.Entry(master=frm_entries)
lbl_postal_code = tk.Label(master=frm_entries, text="Postal Code:")
ent_country = tk.Entry(master=frm_entries)
lbl_country = tk.Label(master=frm_entries, text="Country:")


lbl_first_name.grid(row=0, column=0, sticky="e")
ent_first_name.grid(row=0, column=1, sticky="ew")
lbl_last_name.grid(row=1, column=0, sticky="e")
ent_last_name.grid(row=1, column=1, sticky="ew")
lbl_address_1.grid(row=2, column=0, sticky="e")
ent_address_1.grid(row=2, column=1, sticky="ew")
lbl_address_2.grid(row=3, column=0, sticky="e")
ent_address_2.grid(row=3, column=1, sticky="ew")
lbl_city.grid(row=4, column=0, sticky="e")
ent_city.grid(row=4, column=1, sticky="ew")
lbl_state_province.grid(row=5, column=0, sticky="e")
ent_state_province.grid(row=5, column=1, sticky="ew")
lbl_postal_code.grid(row=6, column=0, sticky="e")
ent_postal_code.grid(row=6, column=1, sticky="ew")
lbl_country.grid(row=7, column=0, sticky="e")
ent_country.grid(row=7, column=1, sticky="ew")

frm_buttons = tk.Frame(master=window, borderwidth=5)
frm_buttons.pack(side=tk.RIGHT)

btn_clear = tk.Button(master=frm_buttons, text="Clear", width=10)
btn_submit = tk.Button(master=frm_buttons,text="Submit", width=10)

btn_clear.grid(row=0, column=0, sticky="e", padx=5)
btn_submit.grid(row=0, column=1, sticky="e", padx=5)


window.mainloop()
