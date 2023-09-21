import matplotlib.pyplot as plt
import numpy as np
import customtkinter as ctk


class ChartWin():
    def create_plt(self , title="" , label=("","") , data= ((0,1,2),(0,1,2)) ,xvertical=False ):
        xpoints , ypoints = np.array(data[0]) , np.array(data[1])
        plt.figure(figsize=(10,6))
        plt.title(title)
        plt.xlabel(label[0])
        plt.ylabel(label[1])
        plt.grid(True)
        if xvertical:
            plt.xticks(rotation='vertical')
        plt.show()
    ###############        ###############        ###############        ###############
    def create_bar(self , title="" , label=("","") , data= ((0,1,2),(0,1,2)) ,xvertical=False  ):
        xpoints , ypoints = np.array(data[0]) , np.array(data[1])
        plt.figure(figsize=(10,6))
        plt.title(title)
        plt.xlabel(label[0])
        plt.ylabel(label[1])
        plt.grid(True)
        if xvertical:
            plt.xticks(rotation='vertical')
        plt.bar(xpoints, ypoints)
        plt.show()

if __name__ == "__main__":
    ChartWin().create_bar()
# import customtkinter as ctk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure
# import numpy as np
# class ChartFrame(ctk.CTkFrame):
#     pass
#     
#         super().__init__(master, fg_color=None)
#         # main container
#         main_frame = ctk.CTkFrame(self , fg_color=None)
#         main_frame.pack(expand=True , fill="both",pady=3,padx=3) 
#         # chart
#         fig = Figure(figsize=(10, 6)) # create a figure object
#         self.ax = fig.add_subplot(111) # add an Axes to the figure
#         self.ax.set_xlabel("Time")
#         self.ax.set_ylabel("Total Price")
#         xpoints = np.array([2, 1, 6, 8])
#         ypoints = np.array([3, 8, 1, 10])
#         self.ax.plot(xpoints, ypoints)
#         self.canvas = FigureCanvasTkAgg(fig,main_frame)
#         self.canvas.get_tk_widget().pack(expand=True , fill="both")
#     ###############        ###############        ###############        ###############
#     def update_data(self,xpoints=[],ypoints=[]):
#         self.ax.clear()
#         xpoints = np.array(xpoints)
#         ypoints = np.array(ypoints)
#         self.ax.plot(xpoints, ypoints)
#         self.canvas.draw()
# ##############################################################################################################