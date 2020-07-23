import win32api, time, os, json

from functions import get_window_region, get_positions, remove_trash
from concurrent.futures.thread import ThreadPoolExecutor


from tkinter import Frame, Button, Spinbox, Toplevel, Checkbutton, BOTH, Tk, IntVar
from PIL import ImageTk
from PIL import Image as PILimage


with open('config.json', 'r') as configfile:
    config_dict= json.load(configfile)






class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.inventory_region = tuple(config_dict["positions"]["inventory_region"])
        self.tabs_positions= config_dict["positions"]["tabs_positions"]
        self.number_of_tabs= IntVar()
        self.number_of_tabs.set(config_dict["vars"]["number_of_tabs"])
        self.player_position= config_dict["positions"]["player_position"]


        trash_list = os.listdir("trash\\")

        try:
            trash_list.remove("Thumbs.db") #~remove Thumbs.db
        except:
            pass

        self.trash_dir_list= trash_list
        self.trash_remove_list=config_dict["lists"]["trash_remove_list"]

        self.init_window()
        

    def init_window(self):
        self.master.title("Metin2 Trash remover")

        self.pack(fill=BOTH, expand=1)





        self.quit_button = Button(self, text="Quit", command=self.client_exit)
        self.quit_button.place(x=0, y=0)

        self.window_coord_button= Button(self, text="Set inventory area", command=self.get_inv_region)  
        self.window_coord_button.place(x=39, y=88)


        self.number_of_tabs_spinbox= Spinbox(self, from_=1, to=5, width=3, textvariable=self.number_of_tabs)
        self.number_of_tabs_spinbox.place(x=21, y=52)

        self.get_tabs_positions_button= Button(self, text="Set Tabs positions", command=self.get_tabs_position)  
        self.get_tabs_positions_button.place(x=64, y=49)   
        self.set_player_positions_button= Button(self, text="Set player position", command=self.get_player_position)
        self.set_player_positions_button.place(x=41, y=127)


        self.run_button= Button(self,text="Run", command=self.destroy_trash_items)
        self.run_button.place(x=78, y=201)


        self.trash_button= Button(self,text="Items to delete", command=self.selector_popup)
        self.trash_button.place(x=49, y=163)


    def selector_popup(self):
        win = Toplevel(self.master)
        win.wm_title("Trash selector")

        j=0    
        i=0

        for item in self.trash_dir_list:
          
            pilImage = PILimage.open(f"trash\\{item}")
            phoImage = ImageTk.PhotoImage(pilImage)
    
            if item in self.trash_remove_list:
                
                #i had a problem using the expression  lambda: self.update_trash_list(item), the problem was that
                #lambda references the memory location of the variable item (i suppose). so we need to bind the item value to a parameter of the lambda.

                cb = Checkbutton(win, image = phoImage,   command=lambda x = item: self.update_trash_list(x))

                cb.select()
                cb.select()
             
            else:
                
                cb = Checkbutton(win, image = phoImage,  command=lambda x = item: self.update_trash_list(x))
        

            #we need to keep a reference of the image, otherwise python garbage collector will make the pictures transparent
            cb.image = phoImage

            cb.grid(row= j, column=i)

            i=i+1
            #with this, each time we pack "x" items, we add one to the row variable 
            if ( i%6 == 5):
                j=j+1
                i=0
       




    def update_trash_list(self, item):
  
        if item in self.trash_remove_list:

            self.trash_remove_list.remove(item)
        else:
            self.trash_remove_list.append(item)




    def client_exit(self):
        exit()  

    def get_inv_region(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            region= executor.submit(get_window_region)
            self.inventory_region=region.result()

    def get_tabs_position(self):


        if self.number_of_tabs is not None:
            with ThreadPoolExecutor(max_workers=1) as executor:
                tabs_func = executor.submit(get_positions, self.number_of_tabs.get())
                self.tabs_positions= tabs_func.result()

            
        else:
            messagebox.showerror("Error", "Change the number of tabs to a valid value")




    def get_player_position(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            pos_func= executor.submit(get_positions, 1) #get_positions expects the number of positions to fetch from the clicks
            self.player_position=pos_func.result()




    def destroy_trash_items(self):

        if self.number_of_tabs is not None  and  self.inventory_region is not None and self.player_position is not None:
            with ThreadPoolExecutor(max_workers=5) as executor:

                remove_func= executor.submit(remove_trash,self.trash_remove_list, self.inventory_region, self.tabs_positions, self.number_of_tabs.get(), self.player_position)
                remove_func.done()

            #after we run the main function we update the config values with the current positions
            with open('config.json', 'w') as configfile:
                
                config_dict['positions']['inventory_region'] = self.inventory_region
                config_dict['positions']['tabs_positions'] = self.tabs_positions
                config_dict['positions']['player_position'] = self.player_position

                config_dict['lists']['trash_remove_list'] = self.trash_remove_list

                config_dict["vars"]["number_of_tabs"] =  self.number_of_tabs.get()


                json.dump(config_dict, configfile)
         
        
        else:
            messagebox.showerror("Error", "Inventory, tabs and player positions are required")       



#if we dont put the main loop inside this check, when we try to use ProcessPoolExecutor multiple instances of the gui are loaded
if __name__ == '__main__':   
    root = Tk()

    root.geometry("200x300")
    app = Window(root)

    root.mainloop()