import pyautogui as pygui 
import pydirectinput as pydirect 
import win32api, time, os, cv2





def get_window_region(screenshot=False):
    left_click=win32api.GetKeyState(0x01) #we need an initial state of the key to check if the state has changed in the loop.

    i=0 
    while True:
        l_click=win32api.GetKeyState(0x01)
        if l_click != left_click:
            left_click=l_click
            if l_click<0 : # GetKeyState returns a negative value if the key is pressed
                if i==0:
                    top_corner_x,top_corner_y=pygui.position()
                    i=i+1
                else:
                    bottom_corner_x,bottom_corner_y=pygui.position()
                    break
        time.sleep(0.01)

                    
    #if the first click is more down or right than the other, we need to change it so we can make a region box
    if top_corner_x > bottom_corner_x: 
        aux = top_corner_x
        top_corner_x = bottom_corner_x
        bottom_corner_x= aux

    if top_corner_y > bottom_corner_y:
        aux = top_corner_y
        top_corner_y = bottom_corner_y
        bottom_corner_y= aux



    box_x=top_corner_x-bottom_corner_x
    box_y=top_corner_y-bottom_corner_y

    region=(top_corner_x,top_corner_y,abs(box_x),abs(box_y))

    if screenshot:
        img= pygui.screenshot(region=region)
        return img
    else:
        return region



def get_positions(clicks):
    left_click=win32api.GetKeyState(0x01)
    positions_list=[]
    i=0 
    while True:
        l_click=win32api.GetKeyState(0x01)
        if l_click != left_click:
            left_click=l_click
            if l_click<0 : # GetKeyState returns a negative value if the key is pressed
                x_, y_ = pygui.position()

                positions_list.append({"x":x_,"y":y_})
                i=i+1
                if i==clicks:
                    break

                    
        time.sleep(0.01)
        
    return positions_list





# inventory tabs is a list with the positions of the diferents inventory tabs, we could do this with the position of a region, but i think is better for compatibility letting the user fix those values.
# also, we need to know the position of the player so we can dump the object without interfering with the other player
# note: player_position is a 1 point list.
def remove_trash(trash_list,inventory_region,inventory_tabs, number_of_tabs, player_position): 


    for i in range(0,number_of_tabs):

        pydirect.click(inventory_tabs[i]['x'],inventory_tabs[i]['y'])


        for item in trash_list:

        
        
            in_inventory_item_list =list(pygui.locateAllOnScreen(f'trash\\{item}',region=inventory_region, confidence=0.9))


            for item_ in in_inventory_item_list:
                print(item_)

                pydirect.click(item_.left+7,item_.top+10)
                pydirect.click(player_position[0]['x'],player_position[0]['y'], clicks=2, interval=0.25)
                
    

        