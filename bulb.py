#Bulb is a simple file explorer for your Tulip Creative Computer!
"""
Find the latest version at https://github.com/KreativKodok/Bulb/
Low effort by Laszlo Andras Halak (kreativkodok)

v0.1 - 2026.05
"""

import os
import ui
import upysh
import tulip
import lvgl as lv

if "WEB" in tulip.board():
    import world_web as world
else:
    import world as world

DIRECTORY = 0x4000
FILE = 0x8000

origin = None
redrawable_area = None
vertical_index = 0

last_location = os.getcwd()

#theme_color = lv.PALETTE.RED
#theme_color = lv.PALETTE.CYAN
theme_color = lv.PALETTE.TEAL
#theme_color = lv.PALETTE.GREY

window_header_text = "Bulb File Explorer v0.1"

template_app = """
#describe your app here

import os
import upysh
import tulip
import math
import random

import music
import midi
import synth
import sequencer
import amy

import lvgl as lv



app = None
window = none



def activate(screen):
    return
    
def deactivate(screen):
    return

def quit(screen):
    return

    
def run(screen):
    lv.init()
    global app = screen
    
    app.quit_callback = quit;
    app.activate_callback = activate;
    app.deactivate_callback = deactivate;
    app.handle_keyboard=True
    
    window = app.group
    
    
    
    app.present()
"""


icon_style = lv.style_t()
icon_style.init()
icon_style.set_bg_color(lv.palette_lighten(lv.PALETTE.GREY, 1))
icon_style.set_text_color(lv.color_black())

dir_style = lv.style_t()
dir_style.init()
dir_style.set_bg_color(lv.palette_lighten(lv.PALETTE.YELLOW, 1))
dir_style.set_text_color(lv.color_black())

icon_pressed_style = lv.style_t()
icon_pressed_style.init()
icon_pressed_style.set_bg_color(lv.palette_darken(lv.PALETTE.GREY, 1))
icon_style.set_text_color(lv.color_white())


field_style = lv.style_t()
field_style.init()
field_style.set_bg_color(lv.color_white())
field_style.set_text_color(lv.color_black())
field_style.set_border_color(lv.color_black())

selected_entity = ''

rubbish_path = '/_compost'

cut_flag = False
copy_path = ''

    


class Icon:
    def __init__(self, parent, file):
        self.button = lv.button(parent)
        self.button.set_size(150,100)
        self.button.set_style_pad_all(5,0)
        label = lv.label(self.button)
        label.set_text(file[0])
        label.set_width(130)
        label.set_height(lv.SIZE_CONTENT)
        #label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        label.set_long_mode(lv.label.LONG.WRAP)
        label.set_pos(5, 5)
        self.button.add_event_cb(lambda e : set_selection(self.button), lv.EVENT.CLICKED, None)
        
        if selected_entity == os.getcwd() + '/' + self.button.get_child(0).get_text():
        	self.button.set_style_outline_width(3,0)
        	self.button.set_style_outline_pad(6, 0)
        
        #print(os.getcwd() + '/' + self.button.get_child(0).get_text())
        mini_icon = lv.label(self.button)
        mini_icon.set_pos(115, 70)
        
        if file[1] & DIRECTORY == DIRECTORY:
            self.button.set_style_bg_color(lv.palette_darken(lv.PALETTE.GREY, 2),0)
            self.button.add_event_cb(lambda e : open_dir_cb(e, self.button), lv.EVENT.LONG_PRESSED, None)
            
            mini_icon.set_text(lv.SYMBOL.DIRECTORY)
   
        else: # is FILE
            self.button.set_style_bg_color(lv.palette_darken(theme_color, 2),0)
            self.button.add_event_cb(lambda e : run_file_cb(e, self.button), lv.EVENT.LONG_PRESSED, None)
            
            mini_icon.set_text(lv.SYMBOL.FILE)
    

def set_selection(target):
    global selected_entity
    selected_entity = os.getcwd() + '/' + target.get_child(0).get_text()
    redraw(redrawable_area)
    #print(selected_entity + ' is selected')
    return

def execute_cb(event):
    print(selected_entity)
    tulip.run(selected_entity.rpartition('/')[2])

def edit_cb(event):
    if os.stat(selected_entity)[0] & DIRECTORY:
        return
    
    if 'edit' in tulip.running_apps:
        return
    
    tulip.edit(selected_entity)
        
        
def copy_recursive(source, to):
    if os.stat(source)[0] & DIRECTORY == DIRECTORY:
        os.mkdir(to)    
        for entry in os.ilistdir(source):
            copy_recursive(f'{source}/{entry[0]}', f'{to}/{entry[0]}')
    else:
        print(source, to)
        upysh.cp(source, to)
        
def send_rubbish_recursive(source):
    print("to", source, rubbish_path)
    copy_recursive(source, f'{rubbish_path}/{source.rpartition('/')[2]}')
    remove_recursive(source)
        
def copy_cb(event):
    if selected_entity == '':
        return
    global cut_flag
    global copy_path
    cut_flag = False
    copy_path = selected_entity

def cut_cb(event):
    if selected_entity == '':
        return
    global cut_flag
    global copy_path
    cut_flag = True
    copy_path = selected_entity

def paste_cb(event):
    new_path = ''
    global copy_path
    
    if copy_path == '':
        #print('empty')
        return
    
    global cut_flag
    
    tokens = copy_path.rpartition('/')
    entity_type = os.stat(copy_path)[0]
    
    new_name = tokens[2]
    counter = 0
    
    while entry_exists_in_cwd(new_name, (entity_type & DIRECTORY)|(entity_type & FILE)):
        
        new_name = f'Copy of {new_name}'
    
    new_path = f'{os.getcwd()}/{new_name}'
    #print(new_path)
        
    copy_recursive(copy_path, new_path)
    
    if cut_flag:
        remove_recursive(copy_path)
    copy_path = new_path
    # could be more robust, further copies are made of the copies, not the originals. could use a cutboard instead?
    cut_flag = False
    redraw(redrawable_area)
    
    
def open_dir_cb(event, target):
    #print(event)
    #print(target.get_child(0).get_text())
    #print(os.getcwd())
    global last_location
    last_location = os.getcwd()
    os.chdir(os.getcwd() + '/' + target.get_child(0).get_text())
    #print(os.getcwd())
    selected_entity = ''
    redraw(redrawable_area)
    
def edit_file_cb(event, target):
    tulip.edit(os.getcwd() + '/' + target.get_child(0).get_text())
    deactivate(origin)
    
def run_file_cb(event, target):
    tulip.run(os.getcwd() + '/' + target.get_child(0).get_text())
    deactivate(origin)
    
def up_dir_cb(event):
    global last_location
    last_location = os.getcwd()
    os.chdir('..')
    redraw(redrawable_area)
    
def back_dir_cb(event):
    global last_location
    next_location = last_location
    last_location = os.getcwd()
    try:
        os.chdir(next_location)
    except OSError: 
        pass
    redraw(redrawable_area)
    
def forward_dir_cb(event, field):
    forward_path = field.get_text()
    try:
        os.stat(forward_path)
    except OSError:
        pass
    else:
        os.chdir(forward_path)
    redraw(redrawable_area)
    
    
def entry_exists_in_cwd(entry_name, entry_type):
    try:
        for e in os.ilistdir(os.getcwd()):
            if e[1] & entry_type == entry_type and e[0] == entry_name:
                return True
                
    except Exception:
        pass
    
    return False

    
    
def test_cb(event):
    print(event)
    
def remove_recursive(path):
    if os.stat(path)[0] & DIRECTORY == DIRECTORY:
        for entry in os.ilistdir(path):
            remove_recursive(f'{path}/{entry[0]}')
        os.rmdir(path)    
            
    else:
        os.remove(path)
    
def response_remove_cb(event, remove_modal):
    global selected_entity
    
    lv.msgbox.close(remove_modal)
    #print(os.stat(selected_entity))
    remove_recursive(selected_entity)
    #send_rubbish_recursive(selected_entity)
    """
    if os.stat(selected_entity)[0] & DIRECTORY == DIRECTORY:
        os.rmdir(selected_entity)
    else:
        os.remove(selected_entity.rpartition('/')[2])
    """
    
    selected_entity = ''
    redraw(redrawable_area)
    
    
def open_remove_cb(event):
    if selected_entity == '':
        return
    remove_modal = lv.msgbox(origin)
    remove_modal.set_width(400)
    #create_dir_modal.add_flag(lv.obj.FLAG.FLOATING)
    #create_dir_modal.add_close_button()
    remove_button = remove_modal.add_footer_button("Remove")
    cancel_button = remove_modal.add_footer_button("Cancel")
    remove_modal.add_title('Remove')
    remove_modal.center()
    
    label = lv.label(remove_modal.get_content())
    label.set_text(f'Remove {selected_entity.rpartition('/')[2]} ?')
    label.align(lv.ALIGN.TOP_MID, 0, 10)
	
    remove_button.add_event_cb(lambda e: response_remove_cb(e, remove_modal), lv.EVENT.CLICKED, None)
    cancel_button.add_event_cb(lambda e: lv.msgbox.close(remove_modal), lv.EVENT.CLICKED, None)

    
    
def response_create_dir_cb(event, field, msgbox):
    
    new_dir_name = ''
    try:
    	new_dir_name = field.get_text()
    except Exception:
    	lv.msgbox.close(msgbox)
        return
    lv.msgbox.close(msgbox)
    
    if new_dir_name.isspace():
        return
    
    name_holder = new_dir_name
    counter = 0
    
    while entry_exists_in_cwd(name_holder, DIRECTORY):
        counter+=1
        name_holder = f'{new_dir_name} ({counter})'
    
    try:
        os.mkdir(os.getcwd()+'/'+ name_holder)
    except Exception:
        pass
   
    redraw(redrawable_area)
    
    
    
def open_create_dir_cb(event):
    create_dir_modal = lv.msgbox(origin)
    create_dir_modal.set_width(400)
    #create_dir_modal.add_flag(lv.obj.FLAG.FLOATING)
    #create_dir_modal.add_close_button()
    create_button = create_dir_modal.add_footer_button("Create")
    cancel_button = create_dir_modal.add_footer_button("Cancel")
    create_dir_modal.add_title('Create New Directory')
    create_dir_modal.center()
    
    text_area = lv.textarea(create_dir_modal.get_content())
    text_area.set_one_line(True)
    text_area.align(lv.ALIGN.TOP_MID, 0, 10)
    
    text_area.add_style(field_style, 0)
    text_area.add_style(field_style, lv.PART.CURSOR | lv.STATE.FOCUSED)
    text_area.set_width(create_dir_modal.get_width()-15)
    text_area.set_text('MyDir')
	
    create_button.add_event_cb(lambda e: response_create_dir_cb(e, text_area, create_dir_modal), lv.EVENT.CLICKED, None)
    cancel_button.add_event_cb(lambda e: lv.msgbox.close(create_dir_modal), lv.EVENT.CLICKED, None)
    
    lv.group_focus_obj(text_area)
    
        

def response_create_file_cb(event, field, msgbox):
    file_name = ''
    try:
    	file_name = field.get_text()
    except Exception:
    	lv.msgbox.close(msgbox)
        return
    lv.msgbox.close(msgbox)
    
    if file_name.isspace():
    	return
    
    tokens = file_name.rpartition('.')
    name_holder = file_name
    counter = 0
    
    while entry_exists_in_cwd(name_holder, FILE):
        counter+=1
        if tokens[0] == '':
            name_holder = f'{tokens[2]} ({counter})'
        else:
            name_holder = f'{tokens[0]} ({counter}).{tokens[2]}'
    
    
    
    #TODO: check if file already exists, create new with incremented number
    try:
    	open(name_holder, 'w').close()
    except Exception:
        pass
    
    redraw(redrawable_area)
    
    
    
def open_create_file_cb(event):
    create_file_modal = lv.msgbox(origin)
    create_file_modal.set_width(400)
    #create_file_modal.add_flag(lv.obj.FLAG.FLOATING)
    #create_file_modal.add_close_button()
    create_button = create_file_modal.add_footer_button("Create")
    cancel_button = create_file_modal.add_footer_button("Cancel")
    create_file_modal.add_title('Create New File')
    create_file_modal.center()
    
    text_area = lv.textarea(create_file_modal.get_content())
    text_area.set_one_line(True)
    text_area.align(lv.ALIGN.TOP_MID, 0, 10)
    
    text_area.add_style(field_style, 0)
    text_area.add_style(field_style, lv.PART.CURSOR | lv.STATE.FOCUSED)
    text_area.set_width(create_file_modal.get_width()-15)
    text_area.set_text('MyScript.py')
	
    create_button.add_event_cb(lambda e: response_create_file_cb(e, text_area, create_file_modal), lv.EVENT.CLICKED, None)
    cancel_button.add_event_cb(lambda e: lv.msgbox.close(create_file_modal), lv.EVENT.CLICKED, None)
    #text_area.add_event_cb(lambda e: input_text_cb(e, text_area), lv.EVENT.VALUE_CHANGED, None)
	
    lv.group_focus_obj(text_area)
    
    
    
def response_create_app_cb(event, field, msgbox):
    
    file_name = ''
    try:
    	file_name = field.get_text()
    except Exception:
    	lv.msgbox.close(msgbox)
        return
    lv.msgbox.close(msgbox)
    
    if file_name.isspace():
    	return
    
    tokens = file_name.rpartition('.')
    name_holder = file_name
    counter = 0
    
    while entry_exists_in_cwd(name_holder, FILE):
        counter+=1
        if tokens[0] == '':
            name_holder = f'{tokens[2]} ({counter})'
        else:
            name_holder = f'{tokens[0]} ({counter}).{tokens[2]}'
    
    
    
    #TODO: check if file already exists, create new with incremented number
    try:
    	file = open(name_holder, 'w')
        file.write(template_app)
        file.close()
    except Exception:
        pass
    
    redraw(redrawable_area)
    
        
    
def open_create_app_cb(event):
    
    create_app_modal = lv.msgbox(origin)
    create_app_modal.set_width(400)
    create_button = create_app_modal.add_footer_button("Create")
    cancel_button = create_app_modal.add_footer_button("Cancel")
    create_app_modal.add_title('Create New App')
    create_app_modal.center()
    
    text_area = lv.textarea(create_app_modal.get_content())
    text_area.set_one_line(True)
    text_area.align(lv.ALIGN.TOP_MID, 0, 10)
    
    text_area.add_style(field_style, 0)
    text_area.add_style(field_style, lv.PART.CURSOR | lv.STATE.FOCUSED)
    text_area.set_width(create_app_modal.get_width()-15)
    text_area.set_text('MyApp.py')
	
    create_button.add_event_cb(lambda e: response_create_app_cb(e, text_area, create_app_modal), lv.EVENT.CLICKED, None)
    cancel_button.add_event_cb(lambda e: lv.msgbox.close(create_app_modal), lv.EVENT.CLICKED, None)
    #text_area.add_event_cb(lambda e: input_text_cb(e, text_area), lv.EVENT.VALUE_CHANGED, None)
	
    lv.group_focus_obj(text_area)
    
    
        

def response_rename_cb(event, field, msgbox):
    file_name = ''
    try:
    	file_name = field.get_text()
    except Exception:
    	lv.msgbox.close(msgbox)
        return
    lv.msgbox.close(msgbox)
    
    old_name = selected_entity.rpartition('/')[2]
    if file_name == old_name:
        return
    
    if file_name.isspace():
    	return
    
    #copy_recursive(selected_entity, f'{os.getcwd()}/{file_name}')
    try:
    	os.rename(selected_entity, file_name)
    except OSError:
            pass
    redraw(redrawable_area)
    
    
    
def open_rename_cb(event):
    if selected_entity == '':
        return
    rename_modal = lv.msgbox(origin)
    rename_modal.set_width(400)
    #create_file_modal.add_flag(lv.obj.FLAG.FLOATING)
    #create_file_modal.add_close_button()
    rename_button = rename_modal.add_footer_button("Rename")
    cancel_button = rename_modal.add_footer_button("Cancel")
    rename_modal.add_title('Rename')
    rename_modal.center()
    
    text_area = lv.textarea(rename_modal.get_content())
    text_area.set_one_line(True)
    text_area.align(lv.ALIGN.TOP_MID, 0, 10)
    
    text_area.add_style(field_style, 0)
    text_area.add_style(field_style, lv.PART.CURSOR | lv.STATE.FOCUSED)
    text_area.set_width(rename_modal.get_width()-15)
    text_area.set_text(selected_entity.rpartition('/')[2])
	
    rename_button.add_event_cb(lambda e: response_rename_cb(e, text_area, rename_modal), lv.EVENT.CLICKED, None)
    cancel_button.add_event_cb(lambda e: lv.msgbox.close(rename_modal), lv.EVENT.CLICKED, None)
    #text_area.add_event_cb(lambda e: input_text_cb(e, text_area), lv.EVENT.VALUE_CHANGED, None)
	
    lv.group_focus_obj(text_area)       

def response_upload_cb(event, file_path, description, msgbox):
    desc = description.get_text()
    lv.msgbox.close(msgbox)
    
    tokens = file_path.rpartition('/')
    os.chdir(tokens[0])
    
    world.upload(tokens[2], desc)
    
    redraw(redrawable_area)
    
    
    
def open_upload_cb(event):
    if selected_entity == '':
        return
    modal = lv.msgbox(origin)
    modal.set_width(400)
    #create_file_modal.add_flag(lv.obj.FLAG.FLOATING)
    #create_file_modal.add_close_button()
    affirm_button = modal.add_footer_button("Upload")
    cancel_button = modal.add_footer_button("Cancel")
    modal.add_title(f'Upload {selected_entity.rpartition('/')[2]} to Tulip World')
    modal.center()
    
    text_area = lv.textarea(modal.get_content())
    text_area.set_one_line(True)
    text_area.align(lv.ALIGN.TOP_MID, 0, 10)
    
    text_area.add_style(field_style, 0)
    text_area.add_style(field_style, lv.PART.CURSOR | lv.STATE.FOCUSED)
    text_area.set_width(modal.get_width()-15)
    text_area.set_placeholder_text("Say something about your file...")
    first_line = open(selected_entity).readline().replace("\n","")
    if '#' in first_line:
        first_line = first_line.split('#')[-1]
        text_area.set_text(first_line)
	
    affirm_button.add_event_cb(lambda e, n = selected_entity, d = text_area, m = modal: response_upload_cb(e, file_path = n, description = d, msgbox = m), lv.EVENT.CLICKED, None)
    cancel_button.add_event_cb(lambda e: lv.msgbox.close(modal), lv.EVENT.CLICKED, None)
    #text_area.add_event_cb(lambda e: input_text_cb(e, text_area), lv.EVENT.VALUE_CHANGED, None)
	
    lv.group_focus_obj(text_area)
    
    
def redraw(area):
    area.clean()
    
    top_row = lv.obj(area)
    top_row.set_size(1024-25, 46)
    top_row.set_style_bg_color(lv.palette_lighten(theme_color, 3), 0)
    top_row.set_style_border_width(0,0)
    top_row.set_style_pad_all(0, 0)
    top_row.set_flex_flow(lv.FLEX_FLOW.ROW)
    
    back_button = lv.button(top_row)
    back_label = lv.label(back_button)
    back_label.set_text(lv.SYMBOL.LEFT)
    back_label.center()
    back_button.set_size(60, 40)
    back_button.add_event_cb(back_dir_cb, lv.EVENT.CLICKED, None)
    back_button.set_style_bg_color(lv.palette_darken(theme_color, 4), 0)
    
    up_button = lv.button(top_row)
    up_label = lv.label(up_button)
    up_label.set_text(lv.SYMBOL.UP)
    up_label.center()
    up_button.set_size(60, 40)
    up_button.add_event_cb(up_dir_cb, lv.EVENT.CLICKED, None)
    up_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
    
    path_field = lv.textarea(top_row)
    path_field.set_one_line(True)
    path_field.set_flex_grow(1)
    path_field.add_text(os.getcwd())
    path_field.add_state(lv.STATE.DEFAULT)
    path_field.add_style(field_style, 0)
    path_field.add_style(field_style, lv.PART.CURSOR | lv.STATE.FOCUSED)
    lv.group_focus_obj(path_field)
    
    fwd_button = lv.button(top_row)
    fwd_label = lv.label(fwd_button)
    fwd_label.set_text(lv.SYMBOL.RIGHT)
    fwd_label.center()
    fwd_button.set_size(60, 40)
    fwd_button.add_event_cb(lambda e: forward_dir_cb(e, path_field), lv.EVENT.CLICKED, None)
    fwd_button.set_style_bg_color(lv.palette_darken(theme_color, 4), 0)
    
    bottom_container = lv.obj(area)
    
    bottom_container.clean()
    bottom_container.set_width(area.get_width()-20)
    bottom_container.set_flex_grow(1)
    bottom_container.set_style_pad_all(0,0)
    bottom_container.set_flex_flow(lv.FLEX_FLOW.ROW)
    
    """
    l_panel = lv.obj(bottom_container)
    l_style = lv.style_t()
    l_style.init()
    l_style.set_border_width(0)
    l_style.set_bg_color(lv.color_white())
    l_panel.add_style(l_style, 0)
    l_panel.set_size(300, 407)
    #l_panel.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    
    global vertical_index
    vertical_index = 0
    discover_recursive(l_panel, '/', 0)
    """
    
    
    
    r_panel = lv.obj(bottom_container)
    r_style = lv.style_t()
    r_style.init()
    r_style.set_border_width(0)
    r_style.set_bg_color(lv.color_white())
    r_style.set_pad_all(14)
    r_panel.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)
    #r_style.set_flex_main_place(lv.FLEX_ALIGN.SPACE_EVENLY)
    #r_style.set_layout(lv.LAYOUT_FLEX.value)
    r_panel.add_style(r_style, 0)
    r_panel.set_flex_grow(1)
    r_panel.set_height(407)
    
    
    
    bottom_row = lv.obj(area)
    bottom_row.set_size(1024-25, 45)
    bottom_row.set_style_bg_color(lv.palette_lighten(theme_color, 3), 0)
    bottom_row.set_style_border_width(0,0)
    bottom_row.set_style_pad_all(0, 0)
    bottom_row.set_flex_flow(lv.FLEX_FLOW.ROW)
    bottom_row.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN,lv.FLEX_ALIGN.SPACE_BETWEEN,lv.FLEX_ALIGN.SPACE_BETWEEN)
    bottom_row.set_style_pad_column(10,0)
    button_wdt = 90
    
    new_folder_button = lv.button(bottom_row)
    folder_label = lv.label(new_folder_button)
    folder_label.set_text(lv.SYMBOL.PLUS + " " + lv.SYMBOL.DIRECTORY)
    folder_label.center()
    new_folder_button.set_height(40)
    new_folder_button.set_flex_grow(1)
    new_folder_button.add_event_cb(open_create_dir_cb, lv.EVENT.CLICKED, None)
    new_folder_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
    
    new_file_button = lv.button(bottom_row)
    file_label = lv.label(new_file_button)
    file_label.set_text(lv.SYMBOL.PLUS + " " + lv.SYMBOL.FILE)
    file_label.center()
    new_file_button.set_height(40)
    new_file_button.set_flex_grow(1)
    new_file_button.add_event_cb(open_create_file_cb, lv.EVENT.CLICKED, None)
    new_file_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
        
    new_app_button = lv.button(bottom_row)
    app_label = lv.label(new_app_button)
    app_label.set_text(lv.SYMBOL.PLUS + " " + lv.SYMBOL.CHARGE)
    app_label.center()
    new_app_button.set_height(40)
    new_app_button.set_flex_grow(1)
    new_app_button.add_event_cb(open_create_app_cb, lv.EVENT.CLICKED, None)
    new_app_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
 
    rename_button = lv.button(bottom_row)
    rename_label = lv.label(rename_button)
    rename_label.set_text(lv.SYMBOL.SHUFFLE)
    rename_label.center()
    rename_button.set_height(40)
    rename_button.set_flex_grow(1)
    rename_button.add_event_cb(open_rename_cb, lv.EVENT.CLICKED, None)
    rename_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
       
    remove_button = lv.button(bottom_row)
    remove_label = lv.label(remove_button)
    remove_label.set_text(lv.SYMBOL.TRASH)
    remove_label.center()
    remove_button.set_height(40)
    remove_button.set_flex_grow(1)
    remove_button.add_event_cb(open_remove_cb, lv.EVENT.CLICKED, None)
    remove_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
        
    copy_button = lv.button(bottom_row)
    copy_label = lv.label(copy_button)
    copy_label.set_text(lv.SYMBOL.COPY)
    copy_label.center()
    copy_button.set_height(40)
    copy_button.set_flex_grow(1)
    copy_button.add_event_cb(copy_cb, lv.EVENT.CLICKED, None)
    copy_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
    
    cut_button = lv.button(bottom_row)
    cut_label = lv.label(cut_button)
    cut_label.set_text(lv.SYMBOL.CUT)
    cut_label.center()
    cut_button.set_height(40)
    cut_button.set_flex_grow(1)
    cut_button.add_event_cb(cut_cb, lv.EVENT.CLICKED, None)
    cut_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
    
    paste_button = lv.button(bottom_row)
    paste_label = lv.label(paste_button)
    paste_label.set_text(lv.SYMBOL.PASTE)
    paste_label.center()
    paste_button.set_height(40)
    paste_button.set_flex_grow(1)
    paste_button.add_event_cb(paste_cb, lv.EVENT.CLICKED, None)
    paste_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
    
    edit_button = lv.button(bottom_row)
    edit_label = lv.label(edit_button)
    edit_label.set_text(lv.SYMBOL.EDIT)
    edit_label.center()
    edit_button.set_height(40)
    edit_button.set_flex_grow(1)
    edit_button.add_event_cb(edit_cb, lv.EVENT.CLICKED, None)
    edit_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
 
    exec_button = lv.button(bottom_row)
    exec_label = lv.label(exec_button)
    exec_label.set_text(lv.SYMBOL.CHARGE)
    exec_label.center()
    exec_button.set_height(40)
    exec_button.set_flex_grow(1)
    exec_button.add_event_cb(execute_cb, lv.EVENT.CLICKED, None)
    exec_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
   
    upload_button = lv.button(bottom_row)
    upload_label = lv.label(upload_button)
    upload_label.set_text(lv.SYMBOL.UPLOAD)
    upload_label.center()
    upload_button.set_height(40)
    upload_button.set_flex_grow(1)
    upload_button.add_event_cb(open_upload_cb, lv.EVENT.CLICKED, None)
    upload_button.set_style_bg_color(lv.palette_darken(theme_color, 2), 0)
   
    
    
    
    icons = []
    for file in os.ilistdir(os.getcwd()):
        icons.append(Icon(r_panel, file))
        
    
def activate(app):
    return
    
def deactivate(app):
    return

def quit(app):
    return

    
def run(app):
    app.quit_callback = quit;
    app.activate_callback = activate;
    app.deactivate_callback = deactivate;
    app.handle_keyboard=True
    
    lv.init()
    
    global origin
    
    """
    global rubbish_path
    try:
        os.stat('/ram')  # do we have a ramdisk?
    except OSError:
        pass
    else:
        rubbish_path = f'/ram{rubbish_path}' # if yes, use it for the rubbish
    
    
    
    try:
        os.stat(rubbish_path) # do we have a rubbish folder?
    except OSError:
        os.mkdir(rubbish_path) # make one if no
    else:
        for entity in os.ilistdir(rubbish_path):
            remove_recursive(f'{rubbish_path}/{entity[0]}') # empty it if yes
   """
    
    
    app.group.set_style_text_font(lv.font_montserrat_18,0)
    window = lv.obj(app.group)
    origin = app
    
    
    win_style = lv.style_t()
    win_style.init()
    win_style.set_bg_color(lv.palette_lighten(theme_color, 1))
    win_style.set_pad_all(0)
    win_style.set_pad_column(0)
    win_style.set_pad_row(0)
    window.add_style(win_style, 0)
    
    
    window.set_size(1024, 600)
    
    window.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    
    title_row = lv.obj(window)
    
    title_style = lv.style_t()
    title_style.init()
    title_style.set_border_width(0)
    title_style.set_bg_color(lv.palette_lighten(theme_color, 1))
    title_row.add_style(title_style,0)
    
    title_row.set_size(1024-5, 35)
    title = lv.label(title_row)
    title.set_text(window_header_text)
    title.set_pos(0, -10)
    
    
    
    
    active_area = lv.obj(window)
    active_area.set_size(1024-5, 545)
    active_style = lv.style_t()
    active_style.init()
    active_style.set_border_width(0)
    active_style.set_bg_color(lv.palette_lighten(theme_color, 3))
    active_style.set_pad_all(10)
    active_area.add_style(active_style,0)
    active_area.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    
    global redrawable_area
    redrawable_area = active_area
    
    
    
    redraw(active_area)
    
    
    app.present()

    
def discover_recursive(parent, path, indentation):
	global vertical_index
	for entry in os.ilistdir(path):
		if entry[1] & DIRECTORY == DIRECTORY:
			button = lv.button(parent)
			button.set_pos(30*indentation, vertical_index * 40)
			button.set_height(30)
			vertical_index += 1
        
			label = lv.label(button)
			label.set_text(entry[0])
			label.set_align(lv.ALIGN.OUT_BOTTOM_LEFT)
			discover_recursive(parent, path + '/' + entry[0], indentation+1)



#current_dir = '/'
#discover_recursive(current_dir, 1)

def add_to_launcher(_ = None, index = 1):
    def inject_entry(event):
        if ui.lv_launcher is not None:
            button = ui.lv_launcher.add_button(lv.SYMBOL.EYE_OPEN, "Bulb File Explorer")
            button.get_child(0).set_style_text_color(lv.palette_lighten(lv.PALETTE.ORANGE,2),0)
            button.move_to_index(index)
            button.add_event_cb(lambda e: tulip.run('bulb'), lv.EVENT.CLICKED, None) 
            
    ui.repl_screen.launcher_button.add_event_cb(lambda e: inject_entry(e), lv.EVENT.CLICKED, None)
    