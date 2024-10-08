# License: GPL-3.0-or-later

bl_info = {
    "name": "Open File Autosaver",
    "blender": (4, 1, 0),
    "category": "System",
    "version": (1, 1, 0),
    "author": "C0rtex5",
    "description": "An add-on for auto-saving Blender files",
    "location": "File > Tool > Open File Autosaver",
    "warning": "This addon will be merged giving an mutli platfrom extension",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
}

import bpy
import threading

# _______________________________________________Autosave Operator_______________________________________________

class OBJECT_OT_autosave(bpy.types.Operator):
    bl_idname = "object.autosave"
    bl_label = "AutoSave"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.wm.save_mainfile()
        self.report({'INFO'}, "File autosaved")
        return {'FINISHED'}

# _______________________________________________Enabler_______________________________________________

def clear_properties():
    del bpy.types.Scene.autosave_enabled
    del bpy.types.Scene.autosave_interval

def update_autosave_status(self, context):
    if context.scene.autosave_enabled:
        AutosaveTimer.start(context.scene.autosave_interval)
    else:
        AutosaveTimer.stop()

# _______________________________________________Autosave Timer_______________________________________________

class AutosaveTimer:
    _timer_thread = None
    _stop_event = threading.Event()

    @classmethod
    def start(cls, interval):
        cls._stop_event.clear()
        if cls._timer_thread is None or not cls._timer_thread.is_alive():
            cls._timer_thread = threading.Thread(target=cls._run, args=(interval,))
            cls._timer_thread.daemon = True
            cls._timer_thread.start()

    @classmethod
    def stop(cls):
        cls._stop_event.set()
        if cls._timer_thread is not None:
            cls._timer_thread.join()

    @classmethod
    def _run(cls, interval):
        while not cls._stop_event.is_set():
            bpy.ops.object.autosave()
            cls._stop_event.wait(interval)

# _______________________________________________Customization_______________________________________________

def init_properties():
    bpy.types.Scene.autosave_enabled = bpy.props.BoolProperty(
        name="Enable Autosave",
        description="Toggle autosave on or off",
        default=False,
        update=update_autosave_status
    )
    bpy.types.Scene.autosave_interval = bpy.props.IntProperty(
        name="Autosave Interval",
        description="Interval in seconds between each autosave",
        default=300,
        min=10,
        max=3600
    )

# _______________________________________________Panel_______________________________________________

class OBJECT_PT_autosave_panel(bpy.types.Panel):
    pass
    bl_label = "AutoSave Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Helper'
    bl_idname = "OBJECT_PT_autosave_panel"
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 1. Enable Autosave checkbox first
        layout.prop(scene, "autosave_enabled", text="Enable Autosave")

        # 2. Autosave Interval second
        layout.prop(scene, "autosave_interval", text="Autosave Interval (seconds)")

        # 3. Save button third
        layout.operator("object.autosave", text="Save Now", icon='FILE_TICK')


    # def draw(self, context):
    #     layout = self.layout
    #     scene = context.scene
    #     row = layout.row()
    #     row.operator("object.autosave", text='Save', icon='FILE_TICK')
    #     """define the layout of the panel"""

    #     layout.prop(scene, "autosave_enabled")
    #     layout.prop(scene, "autosave_interval")
        
        # if scene.autosave_enabled:
        #     layout.label(text="Autosave Settings", icon='FILE_TICK')

# _______________________________________________Register and Unregister_______________________________________________

def register():
    bpy.utils.register_class(OBJECT_OT_autosave)
    bpy.utils.register_class(OBJECT_PT_autosave_panel)
    init_properties()

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_autosave)
    bpy.utils.unregister_class(OBJECT_PT_autosave_panel)
    clear_properties()

if __name__ == "__main__":
    register()