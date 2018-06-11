bl_info = {
    "name": "PolySlim",
    "author": "Richard Sim",
    "version": (1,0,0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool Shelf > Tools",
    "description": "Mesh decimation using the qslim algorithm",
    "warning": "",
    "wiki_url": "https://github.com/richard-sim/PolySlim/wiki",
    "tracker_url": "https://github.com/richard-sim/PolySlim/issues",
    "category": "Mesh",
    "support": "COMMUNITY"
}

import bpy
import math
import mathutils
import os
import sys
import shutil
import filecmp
import ctypes

# https://blender.stackexchange.com/questions/93728/blender-script-run-print-to-console
# import builtins as __builtin__

# def console_print(*args, **kwargs):
#     for a in bpy.context.screen.areas:
#         if a.type == 'CONSOLE':
#             c = {}
#             c['area'] = a
#             c['space_data'] = a.spaces.active
#             c['region'] = a.regions[-1]
#             c['window'] = bpy.context.window
#             c['screen'] = bpy.context.screen
#             s = " ".join([str(arg) for arg in args])
#             for line in s.split("\n"):
#                 bpy.ops.console.scrollback_append(c, text=line)

# def print(*args, **kwargs):
#     """Console print() function."""

#     console_print(*args, **kwargs) # to py consoles
#     __builtin__.print(*args, **kwargs) # to system console


libPolySlim = None


class PSVec3(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)]

class PSFace(ctypes.Structure):
    IndicesType = ctypes.c_int * 3
    _fields_ = [("v", IndicesType)]


class PolySlim_Settings(bpy.types.PropertyGroup):
    targetTriangleCount = bpy.props.IntProperty(name="Triangle Count",
                                                description="Target triangle count for the mesh",
                                                min=1,
                                                soft_min=4)


class DecimateOperator(bpy.types.Operator):
    bl_idname = "polyslim.decimate"
    bl_label = "PolySlim Decimate"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        global libPolySlim
        if libPolySlim is None:
            print("PolySlim shared library not loaded!")
            return {'FINISHED'}
        
        # sel = context.selected_objects
        # act = context.active_object
        # for obj in sel:
        #     if obj != act:
        #         pass


        # #Define vertices, faces, edges
        # verts = [(0,0,0),(0,5,0),(5,5,0),(5,0,0),(0,0,5),(0,5,5),(5,5,5),(5,0,5)]
        # faces = [(0,1,2,3), (7,6,5,4), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
        
        # #Define mesh and object
        # mymesh = bpy.data.meshes.new("Cube")
        # myobject = bpy.data.objects.new("Cube", mymesh)
        
        # #Set location and scene of object
        # myobject.location = bpy.context.scene.cursor_location
        # bpy.context.scene.objects.link(myobject)
        
        # #Create mesh
        # mymesh.from_pydata(verts,[],faces)
        # mymesh.update(calc_edges=True)


        # new_mesh = context.active_object.to_mesh(scene = bpy.context.scene, apply_modifiers = True, settings = 'PREVIEW')


        obj = context.active_object
        
        num_verts = len(obj.data.vertices)

        obj.data.calc_tessface()
        tmp_faces = []
        for tf in obj.data.tessfaces:
            # Treat like a triangle fan (handles tris and quads, and potentially more if that ever happens?)
            i0 = tf.vertices[0]
            i1 = tf.vertices[1]
            for i in range(2, len(tf.vertices)):
                i2 = tf.vertices[i]
                tmp_faces.append((i0, i1, i2))
                i1 = i2
        num_faces = len(tmp_faces)

        VertsType = PSVec3 * num_verts
        FacesType = PSFace * num_faces

        verts = VertsType()
        for i, v in enumerate(obj.data.vertices):
            verts[i] = PSVec3(v.co.x, v.co.y, v.co.z)
        faces = FacesType()
        for i, f in enumerate(tmp_faces):
            faces[i] = PSFace(PSFace.IndicesType(*f))

        target_face_count = context.scene.PolySlim_Settings.targetTriangleCount

        out_vert_count = ctypes.c_int()
        out_face_count = ctypes.c_int()

        print("Running...")
        res = libPolySlim.decimate(verts, 
                                   len(verts), 
                                   faces, 
                                   len(faces), 
                                   target_face_count,
                                   ctypes.byref(out_vert_count), 
                                   ctypes.byref(out_face_count))
        if not res:
            print("Failed.")
        else:
            print("Success. %d verts and %d faces." % (out_vert_count.value, out_face_count.value))
            # for i in range(out_vert_count.value):
            #     print("Vertex %d: (%f, %f, %f)" % (i, verts[i].x, verts[i].y, verts[i].z))
            # for i in range(out_face_count.value):
            #     print("Face %d: [%d, %d, %d]" % (i, faces[i].v[0], faces[i].v[1], faces[i].v[2]))
            self.create_new_obj(context, obj, verts, out_vert_count.value, faces, out_face_count.value)

        return {'FINISHED'}

    def create_new_obj(self, context, orig_obj, c_verts, vert_count, c_faces, face_count):
        #Define vertices, faces, edges
        verts = []
        for i in range(vert_count):
            v = c_verts[i]
            verts.append((v.x, v.y, v.z))
        faces = []
        for i in range(face_count):
            f = c_faces[i]
            faces.append((f.v[0], f.v[1], f.v[2]))
        
        #Define mesh and object
        mymesh = bpy.data.meshes.new("Decimated")
        myobject = bpy.data.objects.new("Decimated", mymesh)
        
        #Set location and scene of object
        myobject.location = context.scene.cursor_location
        context.scene.objects.link(myobject)
        
        #Create mesh
        mymesh.from_pydata(verts,[],faces)
        mymesh.update(calc_edges=True)


class PolySlim_Panel(bpy.types.Panel):
    """PolySlim Panel"""
    bl_label = "PolySlim v" + '.'.join(map(str, bl_info["version"]))
    bl_idname = "PolySlim_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category="Tools"

    def draw(self, context):
        layout = self.layout

        # Icon names: https://docs.blender.org/api/current/bpy.types.UILayout.html
        # <Space> > Icon Viewer
        
        scale = layout.row()
        scale.scale_y = 2
        scale.operator(DecimateOperator.bl_idname, icon = "MOD_DECIM", text = "Decimate")
        box = layout.box()
        box.label("Decimation Options", icon = "FILTER")
        col = box.column(True)
        col.prop(bpy.context.scene.PolySlim_Settings, "targetTriangleCount",
                 text = "Triangle Count",
                 icon="MOD_TRIANGULATE") #MESH_ICOSPHERE
        # col.prop(bpy.context.scene.B2U_Settings,"applyTransform", text = "Apply Transforms",icon="OBJECT_DATA")

        # box.label("Some label", icon = "MOD_TRIANGULATE")
        # row = box.row()
        # col = row.column(True)
        # col.prop(bpy.context.scene.B2U_Settings,"mat_update", text = "Material Update",icon="MATERIAL_DATA")
        
        # col.prop(bpy.context.scene.B2U_Settings,"use_group", text = "Groups as Prefabs",icon="EXPORT")
        # col.prop(bpy.context.scene.B2U_Settings,"use_scene", text = "Scene",icon="SCENE")

        # if(bpy.context.scene.B2U_Settings.use_scene):
        #     col.prop(bpy.context.scene.B2U_Settings,"use_lights", text = "Lights",icon="OUTLINER_OB_LAMP")
        #     col.prop(bpy.context.scene.B2U_Settings,"use_cam", text = "Cameras",icon="CAMERA_DATA")


def register():
    # Base Register
    bpy.utils.register_module(__name__)

    bpy.types.Scene.PolySlim_Settings = bpy.props.PointerProperty(type=PolySlim_Settings)

    # Don't bother with ctypes.util.find_library as it won't look in this 
    # scripts directory (and will use very different paths on every platform)
    if os.name == "nt":
        libname = "polyslim.dll"
    elif os.name == "posix" and sys.platform == "darwin":
        libname = 'libpolyslim.dylib'
    elif os.name == "posix":
        libname = 'libpolyslim.so'
    libpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), libname)
    # print("Library: %s" % libpath)

    global libPolySlim
    libPolySlim = ctypes.cdll.LoadLibrary(libpath)
    # print(libPolySlim)

    if libPolySlim:
        if libPolySlim.decimate:
            libPolySlim.decimate.restype = ctypes.c_bool
            libPolySlim.decimate.argtypes = [ctypes.POINTER(PSVec3), ctypes.c_int, ctypes.POINTER(PSFace), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def unregister():
    # Base Unregister
    bpy.utils.unregister_module(__name__)

    # print("PolySlim unregistered")

if __name__ == "__main__":
    register()